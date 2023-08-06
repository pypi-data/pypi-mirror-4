"""
Copyright (c) 2012, Dominik Schacht
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
OF SUCH DAMAGE.
"""
import copy

class Quidditas(object):
    """ Provide a usable interface for the Quidditas system.
    """

    def __init__(self):
        """ Initiate an instance of the Quidditas system. """
        self.entity_manager = EntityManager(self)
        self.component_manager = ComponentManager(self)
        self.processor_manager = ProcessorManager(self)

        self.add_type_definitions = self.entity_manager.add_type_definitions

        self.entities_to_remove = set()
        self.entities_to_refresh = set()

    def get_entity(self, gid):
        """ Return an entity with the given gid. """
        return self.entity_manager.entities[gid]

    def add_processor(self, processor):
        """ Add the processor to the entity system.
        Return the processor when it was added, None when not. """
        if self.processor_manager.add_processor(processor):
            processor.set_component_manager(self.component_manager)
            processor.set_quidditas(self)
            processor.refresh_entities(self.entity_manager.entities.values())
            return processor
        return None

    def remove_processor(self, processor):
        """ Remove the processor from the entity system. """
        self.processor_manager.remove_processor(processor)

    def create_entity(self, type_name):
        """ Create an entity by its type name.
        Forwarded to the entity manager. """
        entity = self.entity_manager.create_entity(type_name)
        entity.quidditas = self
        self.component_manager.add_components(entity.gid, entity.components)
        self.processor_manager.refresh_entity(entity)
        del(entity.components)
        return entity

    def add_entity(self, entity):
        """ Add a manually created entity to the system.
        Forwarded to the entity manager. """
        self.entity_manager.add_entity(entity)
        entity.quidditas = self

        try:
            self.component_manager.add_components(entity.gid, entity.components)
        except AttributeError:
            # Entity did not have any components cached. Do nothing
            pass

        self.processor_manager.refresh_entity(entity)
        return entity

    def remove_entity_gid(self, gid):
        """ Schedule an entity for removal on next update. """
        if gid not in self.entities_to_remove:
            self.entities_to_remove.add(gid)

    def add_component(self, entity, component):
        """ Add a component to an entity. """
        self.component_manager.add_component(entity.gid, component)
        self.processor_manager.refresh_entity(entity)

    def remove_component(self, entity, component):
        self.component_manager.remove_component(entity.gid, component.__class__)
        self.processor_manager.refresh_entity(entity)

    def update(self, time):
        """ Perform an update step on all processors.
        time -- Time that has passed since last update. """
        if self.entities_to_remove:
            # Notify managers over removed entities.
            self.entity_manager.remove_entities_gid(self.entities_to_remove)
            self.component_manager.remove_entities_gid(self.entities_to_remove)
            self.processor_manager.remove_entities_gid(self.entities_to_remove)
            self.entities_to_remove.clear()
        if self.entities_to_refresh:
            self.entities_to_refresh.clear()

        self.processor_manager.update(time)

class EntityManager(object):
    """ Adds and removes entities from the world, notifies Processors and keeps
    them updated.

    Attributes:
    last_gid -- Id for the next entity that is created or added.
    entities -- Maps ids to entities for all existing entities.
    types -- Maps type names to a list of configured component instances, therefore it
             maps a type name to the prototype of that entity.
    """

    def __init__(self, quidditas):
        """ Create an empty entity manager. """
        self.next_gid = 0
        self.entities = {}
        self.types = {}
        self.quidditas = quidditas

    def create_entity(self, type_name):
        """ Create an entity of the specified type. """
        # Create an entity and add a copy of every component specified in the prototype.
        entity = Entity()
        # TODO: Remove logging
        print "Created entity of type '{}'.".format(type_name)
        entity.components = [copy.copy(comp) for comp in self.types[type_name]]
        entity.components.append(TypeComponent(type_name))
        return self.add_entity(entity)

    def add_entity(self, entity):
        """ Add a manually created entity to the world. """
        entity.gid = self.next_gid
        self.next_gid += 1
        self.entities[entity.gid] = entity
        return entity

    def remove_entities_gid(self, gids):
        """ Remove all entities specified in the list of gids. """
        [self.entities.pop(gid) for gid in gids]

    def remove_entity_gid(self, gid):
        """ Remove an entity from the world by its id. """
        return self.entities.pop(gid)

    def add_type_definitions(self, definitions):
        """ Merge the type definitions with the current type definitions. """
        self.types = dict(self.types.items() + definitions.items())

class ComponentManager(object):
    """ Manages the components and their associations with the existing entities.
    DOCME: attributes and maps """

    def __init__(self, quidditas):
        # {entity_gid => {component_type=>component_instance,..}, ...}
        self.entity_components = {}
        self.component_to_entities = {}
        self.quidditas = quidditas

    def get_entities_with_component(self, component_type):
        """ Return a list of entity-ids that have the given component type associated with them. """
        try:
            return self.component_to_entities[component_type]
        except KeyError:
            return None

    def add_component(self, entity_gid, component):
        """ Add the component to the id->components map. """
        try:
            components = self.entity_components[entity_gid]
            if components.has_key(component.__class__):
                # Component already assigned to this entity. Do something before overwrite?
                pass
            components[component.__class__] = component

        except KeyError:
            # No components assigned yet.
            self.entity_components[entity_gid] = {component.__class__ : component}
        try:
            self.component_to_entities[component.__class__].add(entity_gid)
        except KeyError:
            self.component_to_entities[component.__class__] = set((entity_gid,))

    def add_components(self, entity_gid, new_components):
        """ Add multiple components. """
        try:
            components = self.entity_components[entity_gid]
            for component in new_components:
                if components.has_key(component.__class__):
                    # Component already assigned to this entity. Do something before overwrite?
                    pass
                components[component.__class__] = component
        except KeyError:
            # No components assigned yet.
            self.entity_components[entity_gid] = {comp.__class__: comp for comp in new_components }

        # Add connections to component:[entity_gids] map
        for component in new_components:
            try:
                self.component_to_entities[component.__class__].add(entity_gid)
            except KeyError:
                self.component_to_entities[component.__class__] = set((entity_gid,))

    def remove_component(self, entity_gid, component_type):
        """ Remove a component from an entity. """
        try:
            # FIXME: This is wrong, see the attribute documentation for self.entity_components!
            components = self.entity_components[entity_gid]
            del(components[component_type])
        except KeyError:
            # Invalid entity id
            pass
        try:
            self.component_to_entities[component_type].remove(entity_gid)
        except KeyError:
            # Invalid entity id
            pass

    def remove_entity_gid(self, gid):
        """ React that an entity has been removed. """
        try:
            # remove entity from all component:[entity_gids] lists
            for component in self.entity_components[gid].keys():
                self.component_to_entities[component].remove(gid)

            # then remove it from the entity:[components] map
            del self.entity_components[gid]
        except KeyError:
            # Entity did not have any components. Nothing to do.
            pass

    def remove_entities_gid(self, gids):
        """ Remove all given entities. """
        # TODO: Write list comprehension for this
        for gid in gids:
            for component in self.entity_components[gid].keys():
                self.component_to_entities[component].remove(gid)
            print ""
        [self.entity_components.pop(gid) for gid in gids]

class ProcessorManager(object):
    """ Keeps track of all processors and notifies them of entity-changes.
        Attributes:
          self.processors      - The list of processors that have been registered with this
                                 instance.
          self.processor_types - The types of the registered processors.
          self.quidditas       - The quidditas instance related to this processor manager.
    """

    def __init__(self, quidditas):
        """ Create an empty ProcessorManager. """
        self.processors = []
        self.processor_types = []
        self.quidditas = quidditas

    def update(self, time):
        """ Perform an update step on all processors that have auto_update enabled. """
        # Disabled auto update
        #[processor.update(time) if processor.auto_update else None for processor in self.processors]
        pass

    def add_processor(self, processor):
        """ Add the processor to the entity system.
        Only add processors that have not been added yet. """
        if processor.__class__ not in self.processor_types:
            self.processor_types.append(processor.__class__)
            self.processors.append(processor)
            return True
        return False

    def remove_processor(self, processor):
        """ Remove the processor from the entity system. """
        if processor.__class__ in self.processor_types:
            self.processor_types.remove(processor.__class__)
            self.processors.remove(processor)

    def refresh_entity(self, entity):
        """ Notify all processors when an entity has changed its components. """
        [processor.refresh_entity(entity) for processor in self.processors]

    def remove_entities_gid(self, gids):
        """ Remove the set of entities from all processors. """
        [processor.remove_entities_gid(gids) for processor in self.processors]

class Processor(object):
    """
    Keeps a list of entities that have relevant components and works with these components
    on each update.
        Attributes:
          self.auto_update - Defaults to true, enables the processor manager to
                             automatically update this processor on every update. """

    def __init__(self):
        """
        Create a new processor that operates on the given component types.
        """
        self.component_manager = None
        self.entities = set()
        try:
            if self.component_types is not None and type(self.component_types) is not set:
                self.component_types = set(self.component_types)
        except AttributeError:
            self.component_types = set()

    def set_component_manager(self, manager):
        self.component_manager = manager
        self.entity_components = manager.entity_components

    def set_quidditas(self, q):
        """ Store a reference to the current quidditas instance that this processor was added to. """
        self.quidditas = q

    def refresh_entities(self, entity_list):
        """ Refresh a list of entities at once. """
        [self.refresh_entity(entity) for entity in entity_list]

    def refresh_entity(self, entity):
        """ Check if the entity has all components
        that are relevant to this processor and add
        it to the list of entities in that case.

        When it doesn't and has been an entity of this processor, remove it.

        Calls added() when the entity is added, removed() when it is removed.
        """
        component_types = entity.get_component_types()
        if self.component_types.issubset(set(component_types)):
            self.entities.add(entity)
            self.added(entity)
        elif entity in self.entities:
            self.entities.remove(entity)
            self.removed(entity)

    def update(self, time):
        """ Update all assigned entities. """
        [self.update_entity(time, entity, self.entity_components[entity.gid]) for entity in self.entities]

    def update_entity(self, time, entity, components):
        """ Work with the components of the given entity.
        Component instances are accessed by components[component_type].
        """
        pass

    def added(self, entity):
        """ Called when an entity of interest was added to the world. """
        pass

    def removed(self, entity):
        """ Called when an entity of interest was removed from the world. """
        pass

    def remove_entities_gid(self, gids):
        """ Remove all given entity ids that might be associated with this processor. """
        remove = set([e if e.gid in gids else '' for e in self.entities])
        self.entities = self.entities.difference(remove)

class Entity(object):
    """ A single entity. This is usually never subclassed.
    The id is set by the entity manager.
    """

    def __init__(self, type_name=None):
        """
        Create a new entity with an optional type.
        """
        self.gid = 0
        self.quidditas = None

    def kill(self):
        """ Remove this entity from the current quidditas. """
        self.quidditas.remove_entity_gid(self.gid)

    def add_component(self, component):
        """ Add a component to this entity. """
        try:
            self.quidditas.add_component(self, component)
        except AttributeError:
            # Entity has not yet been added to a system, cache the components for later addition.
            try:
                self.components.append(component)
            except AttributeError:
                self.components = [component,]

    def get_type(self):
        """ Return the type name of this entity or None when no type was defined. """
        try:
            return self.get_component(TypeComponent).type
        except NameError:
            return None

    def remove_component(self, component):
        """ Remove a component from this entity. """
        try:
            self.quidditas.remove_component(self, component)
        except AttributeError:
            # Try removing the component from the cached ones.
            try:
                self.components.remove(component)
            except:
                # This entity does not have any components cached, nothing to remove then.
                return

    def get_component(self, component_type):
        """ Retrieve the component instance for the given component type that is associated with this entity. """
        try:
            return self.quidditas.component_manager.entity_components[self.gid][component_type]
        except KeyError:
            raise LookupError("No component of type " + str(component_type))
        except AttributeError:
            try:
                for component in self.components:
                    if component.__class__ == component_type:
                        return component
            except AttributeError:
                # No component of this type associated with this.s
                raise LookupError("No component of type " + str(component_type))

    def get_component_types(self):
        """ Return the types of all components associated with this entity.
        When the entity has not beed added to a quidditas instance and has no local
        components, an empty list will be returned. """
        try:
            return self.quidditas.component_manager.entity_components[self.gid].keys()
        except KeyError:
            # No Components associated with this entity.
            return ()
        except AttributeError:
            try:
                comps = []
                for comp in self.components:
                    comps.append(comp.__class__)
                return comps
            except AttributeError:
                return ()

class TypeComponent(object):
    """ A default component for every entity containing the type of the entity. """
    def __init__(self, type_name):
        self.type = type_name

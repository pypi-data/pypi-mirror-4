# -*- coding: utf-8 -*-
'''
Created on 28.10.2012

@author: dominik
'''
import logging

from mock import MagicMock, Mock
from unittest import TestCase

import quidditas

##############################################
###               Test Data                ###
##############################################

class TestingComponentA(object):
    updated = 0

class TestingComponentB(object):
    updated = 0

class TestingComponentC(object):
    pass

class TestingProcessorA(quidditas.Processor):
    component_types = (TestingComponentA, )

    def update_entity(self, time, entity, components):
        pass

class TestingProcessorB(quidditas.Processor):
    component_types = (TestingComponentB, TestingComponentA)

class TestingProcessorC(quidditas.Processor):
    pass

##############################################
###              Test Cases                ###
##############################################

class TestQuidditas(TestCase):
    """ Tests the quidditas class. """
    def setUp(self):
        self.q = quidditas.Quidditas()
        self.q.entity_manager = MagicMock()
        self.q.component_manager = MagicMock()
        self.q.processor_manager = MagicMock()

    def test_quidditas_init(self):
        """ Test if all managers are created and have
        the necessary back linkgs. """
        self.q = quidditas.Quidditas()
        assert self.q.entity_manager is not None
        assert self.q.component_manager is not None
        assert self.q.processor_manager is not None
        assert self.q.entity_manager.quidditas is not None
        assert self.q.component_manager.quidditas is not None
        assert self.q.processor_manager.quidditas is not None

    def test_manual_add_entity(self):
        """ Test if an entity that is manually added to the
        world gets accepted into the system and receives
        an id. """
        e = quidditas.Entity()
        self.q.add_entity(e)

        assert e.quidditas is self.q
        self.q.entity_manager.add_entity.assert_called_once_with(e)
        self.q.component_manager.add_components.is_called_once()

    def test_add_entity_by_type(self):
        """ DOCME """
        comp = TestingComponentA()
        entity = Mock()
        entity.components = (comp,)
        self.q.entity_manager = Mock()
        self.q.component_manager = Mock()
        self.q.processor_manager = Mock()
        self.q.entity_manager.create_entity.return_value = entity

        self.q.create_entity("test_type")
        self.q.entity_manager.create_entity.assert_called_with("test_type")
        assert entity.quidditas is self.q
        self.q.component_manager.add_components.assert_called_with(entity.gid, (comp,))
        self.q.processor_manager.refresh_entity.assert_called_with(entity)

    def test_update_call_to_process_manager(self):
        """ Test that the update call is forwarded to the process
        manager. """
        self.q.update(1)
        self.q.processor_manager.update.assert_called_once_with(1)

    def test_add_remove_processor(self):
        """ DOCME """
        proc = TestingProcessorA()
        proc.refresh_entities = MagicMock()
        self.q.processor_manager.add_processor.return_value = True
        entity_list = (quidditas.Entity(),)
        self.q.entity_manager.entities.values.return_value = entity_list

        self.q.add_processor(proc)

        self.q.processor_manager.add_processor.assert_called_once_with(proc)
        assert proc.component_manager is self.q.component_manager
        proc.refresh_entities.assert_called_once_with(entity_list)

    def test_remove_processor(self):
        """ DOCME """
        proc = TestingProcessorA()
        self.q.remove_processor(proc)
        self.q.processor_manager.remove_processor.called_once_with(proc)

    def test_remove_entity_gid(self):
        """ DOCME """
        e = quidditas.Entity()
        self.q.remove_entity_gid(e.gid)

        assert not self.q.entity_manager.remove_entity_gid.called
        assert not self.q.component_manager.remove_entity_gid.called
        assert not self.q.processor_manager.refresh_entity_gid.called

        self.q.update(1)

        self.q.entity_manager.remove_entities_gid.assert_called_once()
        self.q.component_manager.remove_entities_gid.assert_called_once()
        self.q.processor_manager.refresh_entities_gid.assert_called_once()

    def test_add_component(self):
        """ DOCME """
        entity = quidditas.Entity()
        comp = TestingComponentA()
        self.q.add_component(entity, comp)
        self.q.component_manager.add_component.assert_called_once_with(entity.gid, comp)
        self.q.processor_manager.refresh_entity.assert_called_once_with(entity)

    def test_remove_component(self):
        """ DOCME """
        entity = quidditas.Entity()
        comp = TestingComponentA()
        self.q.remove_component(entity, comp)
        self.q.component_manager.remove_component.assert_called_once_with(entity.gid, comp.__class__)
        self.q.processor_manager.refresh_entity.assert_called_once_with(entity)

class TestEntity(TestCase):
    """ Test the behaviour of the entity's functions. """
    def setUp(self):
        self.q = MagicMock()
        self.e = quidditas.Entity()

    def test_kill(self):
        """ Test that the entity is removed from the system on kill. """
        self.e.quidditas = self.q
        self.e.kill()
        self.q.remove_entity_gid.assert_called_once()

    def test_add_component_with_quidditas(self):
        """ Test adding a component to an entity that is registered with a quidditas instance. """
        comp = TestingComponentA()
        self.e.quidditas = self.q
        self.e.add_component(comp)
        with self.assertRaises(AttributeError):
            comp in self.e.components
        self.q.add_component.assert_called_once_with(self.e, comp)

    def test_add_component_without_quidditas(self):
        """ Test entity behaviour when adding components before
        adding the entity to a quidditas instance. """
        comp = TestingComponentA()
        self.e.add_component(comp)
        assert not self.q.add_component.called, "Adding component should not have been forwarded."

    def test_remove_component_with_quidditas(self):
        """ Test the entity behaviour when adding and removing components
        to and from the entity before it is added to a quidditas instance. """
        self.q.remove_component = MagicMock()
        compA = TestingComponentA()
        compB = TestingComponentB()
        self.q.add_entity(self.e)
        self.e.add_component(compA)
        self.e.add_component(compB)
        self.e.remove_component(compA)
        with self.assertRaises(AttributeError):
            compA in self.e.components

        self.q.remove_component.assert_called_once_with(self.e, compA)

    def test_get_component_without_quidditas(self):
        """ DOCME """
        comp = TestingComponentA()
        self.e.remove_component(comp) #Nothing happens

        with self.assertRaises(LookupError):
            # Exception as no component for this type is available.
            self.e.get_component(TestingComponentA)

        self.e.add_component(comp)
        assert self.e.get_component(TestingComponentA) is comp
        assert self.e.get_component(TestingComponentB) is None

    def test_get_component_with_quidditas(self):
        """ DOCME """
        comp = TestingComponentA()
        self.q = quidditas.Quidditas()
        self.q.add_entity(self.e)
        self.e.add_component(comp)
        assert self.e.get_component(TestingComponentA) is comp
        with self.assertRaises(LookupError):
            self.e.get_component(TestingComponentB)

    def test_remove_component_with_quidditas(self):
        """ Test the component removal on an entity that is added to quidditas."""
        compA = TestingComponentA()
        compB = TestingComponentB()
        self.e.add_component(compA)
        self.e.add_component(compB)
        self.e.remove_component(compA)
        assert compA not in self.e.components
        assert compB in self.e.components

    def test_get_component_types_with_quidditas(self):
        """ DOCME """
        compA = TestingComponentA()
        compB = TestingComponentB()
        self.q = quidditas.Quidditas()

        self.q.add_entity(self.e)
        assert self.e.quidditas is self.q

        assert len(self.e.get_component_types()) == 0

        self.e.add_component(compA)
        assert TestingComponentA in self.e.get_component_types()
        assert TestingComponentB not in self.e.get_component_types()

        self.e.add_component(compB)
        assert TestingComponentA in self.e.get_component_types()
        assert TestingComponentB in self.e.get_component_types()

        self.e.remove_component(compA)
        assert TestingComponentA not in self.e.get_component_types()
        assert TestingComponentB in self.e.get_component_types()

    def test_get_component_types_without_quidditas(self):
        """ DOCME """
        compA = TestingComponentA()
        compB = TestingComponentB()

        assert len(self.e.get_component_types()) == 0

        self.e.add_component(compA)
        assert TestingComponentA in self.e.get_component_types()
        assert TestingComponentB not in self.e.get_component_types()

        self.e.add_component(compB)
        assert TestingComponentA in self.e.get_component_types()
        assert TestingComponentB in self.e.get_component_types()

        self.e.remove_component(compA)
        assert TestingComponentA not in self.e.get_component_types()
        assert TestingComponentB in self.e.get_component_types()

class TestComponentManager(TestCase):
    """ DOCME """
    def setUp(self):
        self.q = quidditas.Quidditas()
        self.comp_manager = self.q.component_manager

    def test_add_component(self):
        """ DOCME """
        e = quidditas.Entity()
        comp = TestingComponentA()
        comp2 = TestingComponentA()

        assert not self.comp_manager.entity_components.has_key(e.gid)

        self.comp_manager.add_component(e.gid, comp)
        assert e.gid in self.comp_manager.entity_components.keys()

        components = self.comp_manager.entity_components[e.gid]
        assert comp in components.values()
        assert len(components.values()) == 1

        self.comp_manager.add_component(e.gid, comp2)
        assert comp not in components.values()
        assert comp2 in components.values()
        assert len(components.values()) == 1


    def test_remove_component(self):
        """ DOCME """
        e = quidditas.Entity()
        compA = TestingComponentA()
        compB = TestingComponentB()

        self.comp_manager.add_component(e.gid, compA)
        self.comp_manager.add_component(e.gid, compB)
        assert len(self.comp_manager.entity_components[e.gid].values()) == 2

        self.comp_manager.remove_component(e.gid, compA.__class__)
        components = self.comp_manager.entity_components[e.gid]
        assert compA not in components.values()
        assert compB in components.values()
        self.comp_manager.remove_component(e.gid, compB.__class__)
        self.comp_manager.remove_component(e.gid, compA.__class__) # Nothing happens
        assert compB not in components.values()

    def test_add_components(self):
        """ DOCME """
        entity = quidditas.Entity()
        compA = TestingComponentA()
        compA2 = TestingComponentA()
        compB = TestingComponentB()
        compC = TestingComponentC()

        self.comp_manager.add_components(entity.gid, (compA, compB))
        assert compA in self.comp_manager.entity_components[entity.gid].values()
        assert compB in self.comp_manager.entity_components[entity.gid].values()

        # Merging new components with old
        self.comp_manager.add_components(entity.gid, (compC,))
        assert compA in self.comp_manager.entity_components[entity.gid].values()
        assert compB in self.comp_manager.entity_components[entity.gid].values()
        assert compC in self.comp_manager.entity_components[entity.gid].values()

        # Replacing components
        self.comp_manager.add_components(entity.gid, (compA2,))
        assert compA2 in self.comp_manager.entity_components[entity.gid].values(), "compA2 should have replaced compA"
        assert compA not in self.comp_manager.entity_components[entity.gid].values()

    def test_remove_entity_gid_non_existent(self):
        """ DOCME """
        e = quidditas.Entity()
        self.comp_manager.remove_entity_gid(e.gid)
        # No exception thrown, nothing happens

    def test_remove_entity_gid(self):
        """ DOCME """
        e = quidditas.Entity()
        self.comp_manager.add_component(e.gid, TestingComponentA())
        assert e.gid in self.comp_manager.entity_components.keys()
        self.comp_manager.remove_entity_gid(e.gid)
        assert e.gid not in self.comp_manager.entity_components.keys()

    def test_remove_entities_gid(self):
        """ DOCME """
        e1 = quidditas.Entity()
        e1.gid = 0
        e2 = quidditas.Entity()
        e2.gid = 1

        self.comp_manager.add_component(e1.gid, TestingComponentA())
        self.comp_manager.add_component(e2.gid, TestingComponentA())
        assert e1.gid in self.comp_manager.entity_components.keys()
        assert e2.gid in self.comp_manager.entity_components.keys()

        self.comp_manager.remove_entities_gid((e1.gid, e2.gid))
        assert e1.gid not in self.comp_manager.entity_components.keys()
        assert e2.gid not in self.comp_manager.entity_components.keys()

class TestProcessorManager(TestCase):
    """ Test functionality of ProcessManager. """
    def setUp(self):
        self.q = quidditas.Quidditas()
        self.proc_manager = self.q.processor_manager

    def test_add_processors(self):
        """ DOCME """
        procA = TestingProcessorA()
        procB = TestingProcessorB()
        assert len(self.proc_manager.processors) == 0

        self.proc_manager.add_processor(procA)
        self.proc_manager.add_processor(procB)
        assert procA in self.proc_manager.processors
        assert procB in self.proc_manager.processors
        assert TestingProcessorA in self.proc_manager.processor_types
        assert TestingProcessorB in self.proc_manager.processor_types

    def test_remove_processor(self):
        """ DOCME """
        procA = TestingProcessorA()
        procB = TestingProcessorB()
        self.proc_manager.add_processor(procA)
        self.proc_manager.add_processor(procB)

        self.proc_manager.remove_processor(procB)
        assert procA in self.proc_manager.processors
        assert procB not in self.proc_manager.processors
        self.proc_manager.remove_processor(procB) # Nothing happens
        self.proc_manager.remove_processor(procA)
        assert procA not in self.proc_manager.processors

    def test_update(self):
        """ Test that processors are not automatically updated. """
        procA = TestingProcessorA()
        procB = TestingProcessorB()
        self.proc_manager.add_processor(procA)
        self.proc_manager.add_processor(procB)

        procA.update = MagicMock()
        procB.update = MagicMock()

        self.proc_manager.update(23)

        assert not procA.update.called
        assert not procB.update.called

    def test_refresh_entity(self):
        """ Test that refresh calls are forwarded to all
        assigned processors. """
        procA = TestingProcessorA()
        procB = TestingProcessorB()
        self.proc_manager.add_processor(procA)
        self.proc_manager.add_processor(procB)

        procA.refresh_entity = MagicMock()
        procB.refresh_entity = MagicMock()
        e = quidditas.Entity()

        self.proc_manager.refresh_entity(e)
        procA.refresh_entity.assert_called_once_with(e)
        procB.refresh_entity.assert_called_once_with(e)

        ### Remove one processor and call again.
        procA.refresh_entity = MagicMock()
        procB.refresh_entity = MagicMock()
        self.proc_manager.remove_processor(procB)
        self.proc_manager.refresh_entity(e)
        procA.refresh_entity.assert_called_once_with(e)
        assert not procB.refresh_entity.called

    def test_remove_entities_gid(self):
        """ DOCME """
        procA = MagicMock()
        self.proc_manager.add_processor(procA)
        self.proc_manager.remove_entities_gid(set((1,2,3)))
        procA.remove_entities_gid.assert_called_once_with(set((1,2,3)))

    def test_no_doubled_processor_types(self):
        """ DOCME """
        procA = TestingProcessorA()
        procB = TestingProcessorA()

        self.proc_manager.add_processor(procA)
        self.proc_manager.add_processor(procB)
        assert procA in self.proc_manager.processors
        assert procB not in self.proc_manager.processors
        assert procB.component_manager is None

class TestEntityManager(TestCase):
    """ DOCME """
    def setUp(self):
        self.q = quidditas.Quidditas()
        self.entity_manager = self.q.entity_manager
        self.types = {"typeA" : (TestingComponentA(),),
                      "typeAB" : (TestingComponentA(), TestingComponentB())}

    def test_merging_type_definitions(self):
        """ DOCME """
        self.entity_manager.add_type_definitions(self.types)
        assert "typeB" not in self.entity_manager.types.keys()

        self.entity_manager.add_type_definitions({"typeB":(TestingComponentB(),)})
        assert "typeB" in self.entity_manager.types.keys()
        assert "typeA" in self.entity_manager.types.keys()
        assert "typeAB" in self.entity_manager.types.keys()

    def test_create_entity_by_type(self):
        """ DOCME """
        self.entity_manager.add_type_definitions(self.types)
        with self.assertRaises(KeyError):
            entity = self.entity_manager.create_entity("does_not_exist")

        entityA = self.entity_manager.create_entity("typeA")
        assert entityA is not None
        assert entityA.get_type() == "typeA"
        assert TestingComponentA in entityA.get_component_types()
        assert TestingComponentB not in entityA.get_component_types()

        entityAB = self.entity_manager.create_entity("typeAB")
        assert entityAB.get_type() != "typeA"
        assert entityAB.get_type() == "typeAB"
        assert entityAB is not None, "TypeAB not instantiated."
        assert entityA.get_component(TestingComponentA) is not entityAB.get_component(TestingComponentA)

    def test_remove_entity_gid(self):
        """ DOCME """
        e = quidditas.Entity()
        with self.assertRaises(KeyError):
            self.entity_manager.remove_entity_gid(e.gid)
        self.entity_manager.add_entity(e)
        assert e.gid in self.entity_manager.entities.keys()
        self.entity_manager.remove_entity_gid(e.gid)
        assert e not in self.entity_manager.entities

    def test_remove_entities_gid(self):
        """ DOCME """
        e1 = quidditas.Entity()
        e1.gid = 0
        e2 = quidditas.Entity()
        e2.gid = 1
        self.entity_manager.add_entity(e1)
        self.entity_manager.add_entity(e2)
        assert e1.gid in self.entity_manager.entities.keys()
        assert e2.gid in self.entity_manager.entities.keys()

        self.entity_manager.remove_entities_gid(set((e1.gid, e2.gid)))
        assert e1.gid not in self.entity_manager.entities.keys()
        assert e2.gid not in self.entity_manager.entities.keys()

class TestProcessor(TestCase):
    """ DOCME """
    def setUp(self):
        self.q = quidditas.Quidditas()
        self.procA = TestingProcessorA()
        self.procB = TestingProcessorB()

    def test_init_without_components(self):
        """ Test behaviour of a processor that has no component types associated.
        Processors without component types should be possible as updateable processors
        that don't work on entities but on something else? """
        procC = TestingProcessorC()
        assert len(procC.component_types) == 0

    def test_refresh_entity(self):
        e = quidditas.Entity()
        comp = TestingComponentA()
        e.add_component(comp)

        self.procA.refresh_entity(e)
        logging.debug("Entities of procA: {}".format(self.procA.entities))
        assert e in self.procA.entities

        self.procB.refresh_entity(e)
        logging.debug("Entities of procB: {}".format(self.procB.entities))
        assert e not in self.procB.entities

        e.remove_component(comp)
        self.procA.refresh_entity(e)
        logging.debug("Entities of procA: {}".format(self.procA.entities))
        assert e not in self.procA.entities
        self.procB.refresh_entity(e)
        logging.debug("Entities of procB: {}".format(self.procB.entities))
        assert e not in self.procB.entities

    def test_update(self):
        """ DOCME """
        e = quidditas.Entity()
        self.q.add_entity(e)
        self.q.add_processor(self.procA)
        comp = TestingComponentA()
        e.add_component(comp)
        self.procA.refresh_entity(e)
        self.procA.update_entity = MagicMock()
        self.procA.update(1)
        self.procA.update_entity.assert_called_once_with(1, e, {TestingComponentA:comp})

class TestProcessor(TestCase):
    """ DOCME """
    def setUp(self):
        self.q = quidditas.Quidditas()

    def test_remove_entities_gid(self):
        """ DOCME """
        e1 = quidditas.Entity()
        e1.gid = 0
        e2 = quidditas.Entity()
        e2.gid = 1
        proc = TestingProcessorA()
        proc.entities.add(e1)
        proc.entities.add(e2)
        assert e1 in proc.entities
        assert e2 in proc.entities

        proc.remove_entities_gid(set((e1.gid, e2.gid, 99)))
        assert e1 not in proc.entities
        assert e2 not in proc.entities

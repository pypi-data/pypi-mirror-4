# Copyright 2008-2011 Canonical Ltd.  All rights reserved.

"""Unit tests for the conversion of interfaces into a web service."""

from zope.configuration.config import ConfigurationExecutionError
from zope.component import (
    adapts,
    getMultiAdapter,
    getSiteManager,
    getUtility,
    )
from zope.component.interfaces import ComponentLookupError
from zope.interface import (
    Attribute,
    implements,
    Interface,
    )
from zope.publisher.interfaces.http import IHTTPRequest
from zope.schema import (
    Int,
    TextLine,
    )
from zope.security.checker import (
    MultiChecker,
    ProxyFactory,
    )
from zope.security.management import (
    endInteraction,
    newInteraction,
    )

from lazr.restful.declarations import (
    accessor_for,
    call_with,
    export_as_webservice_entry,
    exported,
    export_read_operation,
    export_write_operation,
    generate_entry_interfaces,
    generate_operation_adapter,
    LAZR_WEBSERVICE_NAME,
    mutator_for,
    operation_for_version,
    operation_parameters,
    operation_returns_collection_of,
    operation_returns_entry,
    )
from lazr.restful.fields import (
    CollectionField,
    Reference,
    )
from lazr.restful.interfaces import (
    IEntry,
    IResourceGETOperation,
    IWebServiceConfiguration,
    )
from lazr.restful.marshallers import SimpleFieldMarshaller
from lazr.restful.metazcml import (
    AttemptToContributeToNonExportedInterface,
    ConflictInContributingInterfaces,
    find_interfaces_and_contributors,
    generate_and_register_webservice_operations,
    )
from lazr.restful._resource import (
    EntryAdapterUtility,
    EntryResource,
    )
from lazr.restful.testing.webservice import TestCaseWithWebServiceFixtures
from lazr.restful.testing.helpers import (
    create_test_module,
    register_test_module,
    )
from lazr.restful.utils import VersionedObject


class ContributingInterfacesTestCase(TestCaseWithWebServiceFixtures):
    """Tests for interfaces that contribute fields/operations to others."""

    def setUp(self):
        super(ContributingInterfacesTestCase, self).setUp()
        sm = getSiteManager()
        sm.registerAdapter(ProductToHasBugsAdapter)
        sm.registerAdapter(ProjectToHasBugsAdapter)
        sm.registerAdapter(ProductToHasBranchesAdapter)
        sm.registerAdapter(DummyFieldMarshaller)
        self.one_zero_request = self.fake_request('1.0')
        self.two_zero_request = self.fake_request('2.0')
        self.product = Product()
        self.project = Project()

    def test_attributes(self):
        # The bug_count field comes from IHasBugs (which IProduct does not
        # provide, although it can be adapted into) but that field is
        # available in the webservice (IEntry) adapter for IProduct, and that
        # adapter knows it needs to adapt the product into an IHasBugs to
        # access .bug_count.
        self.product._bug_count = 10
        register_test_module('testmod', IProduct, IHasBugs)
        adapter = getMultiAdapter((self.product, self.one_zero_request), IEntry)
        self.assertEqual(adapter.bug_count, 10)

    def test_operations(self):
        # Although getBugsCount() is not provided by IProduct, it is available
        # on the webservice adapter as IHasBugs contributes it to IProduct.
        self.product._bug_count = 10
        register_test_module('testmod', IProduct, IHasBugs)
        adapter = getMultiAdapter(
            (self.product, self.one_zero_request),
            IResourceGETOperation, name='getBugsCount')
        self.assertEqual(adapter(), '10')

    def test_accessor_for(self):
        # The accessor_for annotator can be used to mark a method as an
        # accessor for an attribute. This allows methods with bound
        # parameters to be used in place of properties.
        self.product._branches = [
            Branch('A branch'), Branch('Another branch')]
        register_test_module('testmod', IBranch, IProduct, IHasBranches)
        adapter = getMultiAdapter(
            (self.product, self.one_zero_request), IEntry)
        self.assertEqual(adapter.branches, self.product._branches)

    def test_accessor_for_at_n_included_at_n_plus_1(self):
        # An accessor_for, when defined for version N, will also appear
        # in version N+1.
        self.product._branches = [
            Branch('A branch'), Branch('Another branch')]
        register_test_module('testmod', IBranch, IProduct, IHasBranches)
        adapter_10 = getMultiAdapter(
            (self.product, self.one_zero_request), IEntry)
        adapter_20 = getMultiAdapter(
            (self.product, self.two_zero_request), IEntry)
        self.assertEqual(adapter_10.branches, adapter_20.branches)

    def test_only_one_accessor_for_version(self):
        # There can only be one accessor defined for a given attribute
        # at a given version.
        def declare_too_many_accessors():
            class IHasTooManyAccessors(Interface):
                export_as_webservice_entry(contributes_to=[IProduct])
                needs_an_accessor = exported(
                    TextLine(title=u'This needs an accessor', readonly=True))

                @accessor_for(needs_an_accessor)
                def get_whatever_it_is(self):
                    pass

                @accessor_for(needs_an_accessor)
                def get_whatever_it_is_again(self):
                    pass
        self.assertRaises(TypeError, declare_too_many_accessors)

    def test_accessors_can_be_superseded(self):
        # Separate accessors can be declared for different versions of
        # an interface.
        self.product._bug_target_name = "Bug target name"
        register_test_module('testmod', IProduct, IHasBugs)
        adapter_10 = getMultiAdapter(
            (self.product, self.one_zero_request), IEntry)
        adapter_20 = getMultiAdapter(
            (self.product, self.two_zero_request), IEntry)
        self.assertEqual(
            adapter_10.bug_target_name, self.product._bug_target_name)
        self.assertEqual(
            adapter_20.bug_target_name,
            self.product._bug_target_name + " version 2.0")

    def test_accessor_and_mutator_together(self):
        # accessor_for and mutator_for can be used together on a field
        # to present a field that can be manipulated as though it's an
        # attribute whilst using local method calls under-the-hood.
        register_test_module('testmod', IProduct, IHasBugs)
        adapter = getMultiAdapter(
            (self.product, self.one_zero_request), IEntry)
        adapter.bug_target_name = "A bug target name!"
        self.assertEqual(
            "A bug target name!", adapter.context._bug_target_name)
        self.assertEqual("A bug target name!", adapter.bug_target_name)

    def test_contributing_interface_with_differences_between_versions(self):
        # In the '1.0' version, IHasBranches.development_branches is exported
        # with its original name whereas for the '2.0' version it's exported
        # as 'development_branch_20'.
        self.product._dev_branch = Branch('A product branch')
        register_test_module('testmod', IBranch, IProduct, IHasBranches)
        adapter = getMultiAdapter((self.product, self.one_zero_request), IEntry)
        self.assertEqual(adapter.development_branch, self.product._dev_branch)

        adapter = getMultiAdapter(
            (self.product, self.two_zero_request), IEntry)
        self.assertEqual(
            adapter.development_branch_20, self.product._dev_branch)

    def test_mutator_for_just_one_version(self):
        # On the '1.0' version, IHasBranches contributes a read only
        # development_branch field, but on version '2.0' that field can be
        # modified as we define a mutator for it.
        self.product._dev_branch = Branch('A product branch')
        register_test_module('testmod', IBranch, IProduct, IHasBranches)
        adapter = getMultiAdapter((self.product, self.one_zero_request), IEntry)
        try:
            adapter.development_branch = None
        except AttributeError:
            pass
        else:
            self.fail('IHasBranches.development_branch should be read-only '
                      'on the 1.0 version')

        adapter = getMultiAdapter(
            (self.product, self.two_zero_request), IEntry)
        self.assertEqual(
            adapter.development_branch_20, self.product._dev_branch)
        adapter.development_branch_20 = None
        self.assertEqual(
            adapter.development_branch_20, None)

    def test_contributing_to_multiple_interfaces(self):
        # Check that the webservice adapter for both IProduct and IProject
        # have the IHasBugs attributes, as that interface contributes to them.
        self.product._bug_count = 10
        self.project._bug_count = 100
        register_test_module('testmod', IProduct, IProject, IHasBugs)
        adapter = getMultiAdapter((self.product, self.one_zero_request), IEntry)
        self.assertEqual(adapter.bug_count, 10)

        adapter = getMultiAdapter((self.project, self.one_zero_request), IEntry)
        self.assertEqual(adapter.bug_count, 100)

    def test_multiple_contributing_interfaces(self):
        # Check that the webservice adapter for IProduct has the attributes
        # from both IHasBugs and IHasBranches.
        self.product._bug_count = 10
        self.product._dev_branch = Branch('A product branch')
        register_test_module(
            'testmod', IBranch, IProduct, IHasBugs, IHasBranches)
        adapter = getMultiAdapter((self.product, self.one_zero_request), IEntry)
        self.assertEqual(adapter.bug_count, 10)
        self.assertEqual(adapter.development_branch, self.product._dev_branch)

    def test_redacted_fields_for_empty_entry(self):
        # An entry which doesn't export any fields/operations will have no
        # redacted fields.
        class IEmpty(Interface):
            export_as_webservice_entry()
        class Empty:
            implements(IEmpty)
        register_test_module('testmod', IEmpty)
        entry_resource = EntryResource(Empty(), self.one_zero_request)
        self.assertEquals({}, entry_resource.entry._orig_interfaces)
        self.assertEquals([], entry_resource.redacted_fields)

    def test_redacted_fields_with_no_permission_checker(self):
        # When looking up an entry's redacted_fields, we take into account the
        # interface where the field is defined and adapt the context to that
        # interface before accessing that field.
        register_test_module(
            'testmod', IBranch, IProduct, IHasBugs, IHasBranches)
        entry_resource = EntryResource(self.product, self.one_zero_request)
        self.assertEquals([], entry_resource.redacted_fields)

    def test_redacted_fields_with_permission_checker(self):
        # When looking up an entry's redacted_fields for an object which is
        # security proxied, we use the security checker for the interface
        # where the field is defined.
        register_test_module(
            'testmod', IBranch, IProduct, IHasBugs, IHasBranches)
        newInteraction()
        try:
            secure_product = ProxyFactory(
                self.product,
                checker=MultiChecker([(IProduct, 'zope.Public')]))
            entry_resource = EntryResource(secure_product, self.one_zero_request)
            self.assertEquals([], entry_resource.redacted_fields)
        finally:
            endInteraction()

    def test_duplicate_contributed_attributes(self):
        # We do not allow a given attribute to be contributed to a given
        # interface by more than one contributing interface.
        testmod = create_test_module(
            'testmod', IBranch, IProduct, IHasBugs, IHasBugs2)
        self.assertRaises(
            ConflictInContributingInterfaces,
            find_interfaces_and_contributors, testmod)

    def test_contributing_interface_not_exported(self):
        # Contributing interfaces are not exported by themselves -- they only
        # contribute their exported fields/operations to other entries.
        class DummyHasBranches:
            implements(IHasBranches)
        dummy = DummyHasBranches()
        register_test_module('testmod', IBranch, IProduct, IHasBranches)
        self.assertRaises(
            ComponentLookupError,
            getMultiAdapter, (dummy, self.one_zero_request), IEntry)

    def test_cannot_contribute_to_non_exported_interface(self):
        # A contributing interface can only contribute to exported interfaces.
        class INotExported(Interface):
            pass
        class IContributor(Interface):
            export_as_webservice_entry(contributes_to=[INotExported])
            title = exported(TextLine(title=u'The project title'))
        testmod = create_test_module('testmod', IContributor, INotExported)
        self.assertRaises(
            AttemptToContributeToNonExportedInterface,
            find_interfaces_and_contributors, testmod)

    def test_duplicate_contributed_methods(self):
        # We do not allow a given method to be contributed to a given
        # interface by more than one contributing interface.
        testmod = create_test_module('testmod', IProduct, IHasBugs, IHasBugs3)
        self.assertRaises(
            ConflictInContributingInterfaces,
            find_interfaces_and_contributors, testmod)

    def test_ConflictInContributingInterfaces(self):
        # The ConflictInContributingInterfaces exception states what are the
        # contributing interfaces that caused the conflict.
        e = ConflictInContributingInterfaces('foo', [IHasBugs, IHasBugs2])
        expected_msg = ("'foo' is exported in more than one contributing "
                        "interface: IHasBugs, IHasBugs2")
        self.assertEquals(str(e), expected_msg)

    def test_type_name(self):
        # Even though the generated adapters will contain stuff from various
        # different adapters, its type name is that of the main interface and
        # not one of its contributors.
        register_test_module('testmod', IProduct, IHasBugs)
        adapter = getMultiAdapter((self.product, self.one_zero_request), IEntry)
        self.assertEqual(
            'product', EntryAdapterUtility(adapter.__class__).singular_type)


class IProduct(Interface):
    export_as_webservice_entry()
    title = exported(TextLine(title=u'The product title'))
    # Need to define the three attributes below because we have a test which
    # wraps a Product object with a security proxy and later uses adapters
    # that access _dev_branch, _branches and _bug_count.
    _dev_branch = Attribute('dev branch')
    _bug_count = Attribute('bug count')
    _branches = Attribute('branches')
    _bug_target_name = Attribute('bug_target_name')


class Product(object):
    implements(IProduct)
    title = 'A product'
    _bug_count = 0
    _dev_branch = None
    _branches = []
    _bug_target_name = None


class IProject(Interface):
    export_as_webservice_entry()
    title = exported(TextLine(title=u'The project title'))


class Project(object):
    implements(IProject)
    title = 'A project'
    _bug_count = 0


class IHasBugs(Interface):
    export_as_webservice_entry(contributes_to=[IProduct, IProject])
    bug_count = exported(Int(title=u'Number of bugs'))
    not_exported = TextLine(title=u'Not exported')
    bug_target_name = exported(
        TextLine(title=u"The bug target name of this object.", readonly=True))

    @export_read_operation()
    def getBugsCount():
        pass

    @mutator_for(bug_target_name)
    @export_write_operation()
    @call_with(bound_variable="A string")
    @operation_parameters(
        bound_variable=TextLine(), new_value=TextLine())
    @operation_for_version('1.0')
    def set_bug_target_name(new_value, bound_variable):
        pass

    @accessor_for(bug_target_name)
    @call_with(bound_value="A string")
    @export_read_operation()
    @operation_parameters(bound_value=TextLine())
    @operation_for_version('1.0')
    def get_bug_target_name(bound_value):
        pass

    @accessor_for(bug_target_name)
    @call_with(bound_value="A string")
    @export_read_operation()
    @operation_parameters(bound_value=TextLine())
    @operation_for_version('2.0')
    def get_bug_target_name_20(bound_value):
        pass


class IHasBugs2(Interface):
    export_as_webservice_entry(contributes_to=[IProduct])
    bug_count = exported(Int(title=u'Number of bugs'))
    not_exported = TextLine(title=u'Not exported')


class IHasBugs3(Interface):
    export_as_webservice_entry(contributes_to=[IProduct])
    not_exported = TextLine(title=u'Not exported')

    @export_read_operation()
    def getBugsCount():
        pass


class ProductToHasBugsAdapter(object):
    adapts(IProduct)
    implements(IHasBugs)

    def __init__(self, context):
        self.context = context
        self.bug_count = context._bug_count

    def getBugsCount(self):
        return self.bug_count

    def get_bug_target_name(self, bound_value):
        return self.context._bug_target_name

    def get_bug_target_name_20(self, bound_value):
        return self.context._bug_target_name + " version 2.0"

    def set_bug_target_name(self, value, bound_variable):
        self.context._bug_target_name = value


class ProjectToHasBugsAdapter(ProductToHasBugsAdapter):
    adapts(IProject)


class IBranch(Interface):
    export_as_webservice_entry()
    name = TextLine(title=u'The branch name')


class Branch(object):
    implements(IBranch)

    def __init__(self, name):
        self.name = name


class IHasBranches(Interface):
    export_as_webservice_entry(contributes_to=[IProduct])
    not_exported = TextLine(title=u'Not exported')
    development_branch = exported(
        Reference(schema=IBranch, readonly=True),
        ('2.0', dict(exported_as='development_branch_20')),
        ('1.0', dict(exported_as='development_branch')))
    branches = exported(
        CollectionField(
            value_type=Reference(schema=IBranch, readonly=True)))

    @mutator_for(development_branch)
    @export_write_operation()
    @operation_parameters(value=TextLine())
    @operation_for_version('2.0')
    def set_dev_branch(value):
        pass

    @accessor_for(branches)
    @call_with(value="A string")
    @export_read_operation()
    @operation_parameters(value=TextLine())
    def get_branches(value):
        pass


class ProductToHasBranchesAdapter(object):
    adapts(IProduct)
    implements(IHasBranches)

    def __init__(self, context):
        self.context = context

    @property
    def development_branch(self):
        return self.context._dev_branch

    def set_dev_branch(self, value):
        self.context._dev_branch = value

    def get_branches(self, value):
        return self.context._branches


# One of our tests will try to unmarshall some entries, but even though we
# don't care about the unmarshalling itself, we need to register a generic
# marshaller so that the adapter lookup doesn't fail and cause an error on the
# test.
class DummyFieldMarshaller(SimpleFieldMarshaller):
    adapts(Interface, IHTTPRequest)

# Classes for TestEntryMultiversion.

class INotInitiallyExported(Interface):
    # An entry that's not exported in the first version of the web
    # service.
    export_as_webservice_entry(as_of="2.0")


class INotPresentInLaterVersion(Interface):
    # An entry that's only exported in the first version of the web
    # service.
    export_as_webservice_entry(
        versioned_annotations=[('2.0', dict(exported=False))])


class IHasDifferentNamesInDifferentVersions(Interface):
    # An entry that has different names in different versions.
    export_as_webservice_entry(
        singular_name="octopus", plural_name="octopi",
        versioned_annotations=[
            ('2.0', dict(singular_name="fish", plural_name="fishes"))])


class IHasDifferentSingularNamesInDifferentVersions(Interface):
    # An entry that has different names in different versions.
    export_as_webservice_entry(
        singular_name="frog",
        versioned_annotations=[('2.0', dict(singular_name="toad"))])


class TestEntryMultiversion(TestCaseWithWebServiceFixtures):
    """Test the ability to export an entry only in certain versions."""

    def test_not_initially_exported(self):
        # INotInitiallyExported is published in version 2.0 but not in 1.0.
        interfaces = generate_entry_interfaces(
            INotInitiallyExported, [],
            *getUtility(IWebServiceConfiguration).active_versions)
        self.assertEquals(len(interfaces), 1)
        self.assertEquals(interfaces[0].version, '2.0')

    def test_not_exported_in_later_version(self):
        # INotPresentInLaterVersion is published in version 1.0 but
        # not in 2.0.
        interfaces = generate_entry_interfaces(
            INotPresentInLaterVersion, [],
            *getUtility(IWebServiceConfiguration).active_versions)
        self.assertEquals(len(interfaces), 1)
        tags = interfaces[0][1].getTaggedValue(LAZR_WEBSERVICE_NAME)
        self.assertEquals(interfaces[0].version, '1.0')

    def test_different_names_in_different_versions(self):
        # IHasDifferentNamesInDifferentVersions is called
        # octopus/octopi in 1.0, and fish/fishes in 2.0.
        interfaces = generate_entry_interfaces(
            IHasDifferentNamesInDifferentVersions, [],
            *getUtility(IWebServiceConfiguration).active_versions)
        interface_10 = interfaces[0].object
        tags_10 = interface_10.getTaggedValue(LAZR_WEBSERVICE_NAME)
        self.assertEquals('octopus', tags_10['singular'])
        self.assertEquals('octopi', tags_10['plural'])

        interface_20 = interfaces[1].object
        tags_20 = interface_20.getTaggedValue(LAZR_WEBSERVICE_NAME)
        self.assertEquals('fish', tags_20['singular'])
        self.assertEquals('fishes', tags_20['plural'])

    def test_nonexistent_annotation_fails(self):
        # You can't define an entry class that includes an unrecognized
        # annotation in its versioned_annotations.
        try:
            class IUsesNonexistentAnnotation(Interface):
                export_as_webservice_entry(
                    versioned_annotations=[
                        ('2.0', dict(no_such_annotation=True))])
            self.fail("Expected ValueError.")
        except ValueError, exception:
            self.assertEquals(
                str(exception),
                'Unrecognized annotation for version "2.0": '
                '"no_such_annotation"')

    def test_changing_singular_also_changes_plural(self):
        # IHasDifferentSingularNamesInDifferentVersions defines the
        # singular name 'frog' in 1.0, and 'toad' in 2.0. This test
        # makes sure that the plural of 'toad' is not 'frogs'.
        interfaces = generate_entry_interfaces(
            IHasDifferentSingularNamesInDifferentVersions, [],
            *getUtility(IWebServiceConfiguration).active_versions)
        interface_10 = interfaces[0].object
        tags_10 = interface_10.getTaggedValue(LAZR_WEBSERVICE_NAME)
        self.assertEquals('frog', tags_10['singular'])
        self.assertEquals('frogs', tags_10['plural'])

        interface_20 = interfaces[1].object
        tags_20 = interface_20.getTaggedValue(LAZR_WEBSERVICE_NAME)
        self.assertEquals('toad', tags_20['singular'])
        self.assertEquals('toads', tags_20['plural'])


# Classes for TestReqireExplicitVersions

class IEntryExportedWithoutAsOf(Interface):
    export_as_webservice_entry()


class IEntryExportedWithAsOf(Interface):
    export_as_webservice_entry(as_of="1.0")


class IEntryExportedAsOfLaterVersion(Interface):
    export_as_webservice_entry(as_of="2.0")


class IFieldExportedWithoutAsOf(Interface):
    export_as_webservice_entry(as_of="1.0")

    field = exported(TextLine(), exported=True)


class IFieldExportedToEarliestVersionUsingAsOf(Interface):
    export_as_webservice_entry(as_of="1.0")

    field = exported(TextLine(), as_of='1.0')


class IFieldExportedToLatestVersionUsingAsOf(Interface):
    export_as_webservice_entry(as_of="1.0")

    field = exported(TextLine(), as_of='2.0')


class IFieldDefiningAttributesBeforeAsOf(Interface):
    export_as_webservice_entry(as_of="1.0")

    field = exported(TextLine(), ('1.0', dict(exported=True)),
                     as_of='2.0')

class IFieldAsOfNonexistentVersion(Interface):
    export_as_webservice_entry(as_of="1.0")

    field = exported(TextLine(), as_of='nosuchversion')


class IFieldDoubleDefinition(Interface):
    export_as_webservice_entry(as_of="1.0")

    field = exported(TextLine(), ('2.0', dict(exported_as='name2')),
                     exported_as='name2', as_of='2.0')


class IFieldImplicitOperationDefinition(Interface):
    export_as_webservice_entry(as_of="1.0")

    @call_with(value="2.0")
    @operation_for_version('2.0')
    @call_with(value="1.0")
    @export_read_operation()
    def implicitly_in_10(value):
        pass


class IFieldExplicitOperationDefinition(Interface):
    export_as_webservice_entry(as_of="1.0")

    @call_with(value="2.0")
    @operation_for_version('2.0')
    @call_with(value="1.0")
    @export_read_operation()
    @operation_for_version('1.0')
    def explicitly_in_10(value):
        pass


class FieldExplicitOperationDefinition(object):
    implements(IFieldExplicitOperationDefinition)


class TestRequireExplicitVersions(TestCaseWithWebServiceFixtures):
    """Test behavior when require_explicit_versions is True."""

    def setUp(self):
        super(TestRequireExplicitVersions, self).setUp()
        self.utility = getUtility(IWebServiceConfiguration)
        self.utility.require_explicit_versions = True

    def test_entry_exported_with_as_of_succeeds(self):
        # An entry exported using as_of is present in the as_of_version
        # and in subsequent versions.
        interfaces = generate_entry_interfaces(
            IEntryExportedWithAsOf, [],
            *self.utility.active_versions)
        self.assertEquals(len(interfaces), 2)
        self.assertEquals(interfaces[0].version, '1.0')
        self.assertEquals(interfaces[1].version, '2.0')

    def test_entry_exported_as_of_later_version_succeeds(self):
        # An entry exported as_of a later version is not present in
        # earlier versions.
        interfaces = generate_entry_interfaces(
            IEntryExportedAsOfLaterVersion, [],
            *self.utility.active_versions)
        self.assertEquals(len(interfaces), 1)
        self.assertEquals(interfaces[0].version, '2.0')

    def test_entry_exported_without_as_of_fails(self):
        exception = self.assertRaises(
            ValueError, generate_entry_interfaces,
            IEntryExportedWithoutAsOf, [],
            *self.utility.active_versions)
        self.assertEquals(
            str(exception),
            'Entry "IEntryExportedWithoutAsOf": Exported in version 1.0, '
            'but not by using as_of. The service configuration requires '
            'that you use as_of.')


    def test_field_exported_as_of_earlier_version_is_exported_in_subsequent_versions(self):
        # If you export a field as_of version 1.0, it's present in
        # 1.0's version of the entry and in all subsequent versions.
        interfaces = generate_entry_interfaces(
            IFieldExportedToEarliestVersionUsingAsOf, [],
            *self.utility.active_versions)
        interface_10 = interfaces[0].object
        interface_20 = interfaces[1].object
        self.assertEquals(interface_10.names(), ['field'])
        self.assertEquals(interface_20.names(), ['field'])

    def test_field_exported_as_of_later_version_is_not_exported_in_earlier_versions(self):
        # If you export a field as_of version 2.0, it's not present in
        # 1.0's version of the entry.
        interfaces = generate_entry_interfaces(
            IFieldExportedToLatestVersionUsingAsOf, [],
            *self.utility.active_versions)
        interface_10 = interfaces[0].object
        interface_20 = interfaces[1].object
        self.assertEquals(interface_10.names(), [])
        self.assertEquals(interface_20.names(), ['field'])

    def test_field_not_exported_using_as_of_fails(self):
        # If you export a field without specifying as_of, you get an
        # error.
        exception = self.assertRaises(
            ValueError, generate_entry_interfaces,
            IFieldExportedWithoutAsOf, [], *self.utility.active_versions)
        self.assertEquals(
            str(exception),
            ('Field "field" in interface "IFieldExportedWithoutAsOf": '
             'Exported in version 1.0, but not by using as_of. '
             'The service configuration requires that you use as_of.')
            )

    def test_field_cannot_be_both_exported_and_not_exported(self):
        # If you use the as_of keyword argument, you can't also set
        # the exported keyword argument to False.
        exception = self.assertRaises(
            ValueError, exported, TextLine(), as_of='1.0', exported=False)
        self.assertEquals(
                str(exception),
                ('as_of=1.0 says to export TextLine, but exported=False '
                 'says not to.'))

    def test_field_exported_as_of_nonexistent_version_fails(self):
        # You can't export a field as_of a nonexistent version.
        exception = self.assertRaises(
            ValueError, generate_entry_interfaces,
            IFieldAsOfNonexistentVersion, [],
            *self.utility.active_versions)
        self.assertEquals(
            str(exception),
            ('Field "field" in interface "IFieldAsOfNonexistentVersion": '
             'Unrecognized version "nosuchversion".'))

    def test_field_exported_with_duplicate_attributes_fails(self):
        # You can't provide a dictionary of attributes for the
        # version specified in as_of.
        exception = self.assertRaises(
            ValueError, generate_entry_interfaces,
            IFieldDoubleDefinition, [], *self.utility.active_versions)
        self.assertEquals(
            str(exception),
            ('Field "field" in interface "IFieldDoubleDefinition": '
             'Duplicate definitions for version "2.0".'))

    def test_field_with_annotations_that_precede_as_of_fails(self):
        # You can't provide a dictionary of attributes for a version
        # preceding the version specified in as_of.
        exception = self.assertRaises(
            ValueError, generate_entry_interfaces,
            IFieldDefiningAttributesBeforeAsOf, [],
            *self.utility.active_versions)
        self.assertEquals(
            str(exception),
            ('Field "field" in interface '
             '"IFieldDefiningAttributesBeforeAsOf": Version "1.0" defined '
             'after the later version "2.0".'))

    def test_generate_operation_adapter_for_none_fails(self):
        # You can't pass None as the version to
        # generate_operation_adapter(). This doesn't happen in normal
        # usage because the metazcml will always pass in a real
        # version number, but we test it just to make sure it'll catch
        # the problem.
        method = [method for name, method in
                  IFieldImplicitOperationDefinition.namesAndDescriptions()
                  if name == 'implicitly_in_10'][0]
        exception = self.assertRaises(
            ValueError, generate_operation_adapter, method, None)
        self.assertEquals(
            str(exception),
            '"implicitly_in_10" is implicitly tagged for export to web '
            'service version "1.0", but the service configuration requires '
            'all version declarations to be explicit. You should add '
            '@operation_for_version("1.0") to the bottom of the '
            'annotation stack.')

    def test_operation_implicitly_exported_in_earliest_version_fails(self):
        # You can't implicitly define an operation for the earliest version.
        exception = self.assertRaises(
            ValueError, generate_and_register_webservice_operations,
            None, IFieldImplicitOperationDefinition, [])
        self.assertEquals(
            str(exception),
            ('IFieldImplicitOperationDefinition.implicitly_in_10: '
             'Implicitly tagged for export to web service version "1.0", '
             'but the service configuration requires all version '
             'declarations to be explicit. You should add '
             '@operation_for_version("1.0") to the bottom of the '
             'annotation stack.'))

    def test_operation_explicitly_exported_in_earliest_version_succeeds(self):
        # You can explicitly define an operation for the earliest version.

        # Unlike the previous test, we can't just call
        # generate_and_register_webservice_operations: we need to have
        # a ZCML context.
        register_test_module('testmod', IFieldExplicitOperationDefinition)
        context = FieldExplicitOperationDefinition()
        adapter = getMultiAdapter(
            (context, self.fake_request('1.0')),
            IResourceGETOperation, name='explicitly_in_10')
        self.assertEquals(
            adapter.__class__.__name__,
            'GET_IFieldExplicitOperationDefinition_explicitly_in_10_1_0')


# Classes for TestSanityChecking

class INotPublished(Interface):
    pass


class IReferencesNotPublished(Interface):
    export_as_webservice_entry()
    field = exported(Reference(schema=INotPublished))


class IReferencesCollectionOfNotPublished(Interface):
    export_as_webservice_entry()
    field = exported(
        CollectionField(value_type=Reference(schema=INotPublished)))


class IOperationReturnsNotPublished(Interface):
    export_as_webservice_entry()

    @operation_returns_entry(INotPublished)
    @export_read_operation()
    def get_impossible_object():
        pass


class IOperationReturnsNotPublishedCollection(Interface):
    export_as_webservice_entry()

    @operation_returns_collection_of(INotPublished)
    @export_read_operation()
    def get_impossible_objects():
        pass


class IOperationAcceptsNotPublished(Interface):
    export_as_webservice_entry()

    @operation_parameters(arg=Reference(schema=INotPublished))
    @export_write_operation()
    def use_impossible_object(arg):
        pass


class IOperationAcceptsCollectionOfNotPublished(Interface):
    export_as_webservice_entry()

    @operation_parameters(
        arg=CollectionField(value_type=Reference(schema=INotPublished)))
    @export_write_operation()
    def use_impossible_objects(arg):
        pass


class IPublishedTooLate(Interface):
    export_as_webservice_entry(as_of='2.0')


class IReferencesPublishedTooLate(Interface):
    export_as_webservice_entry(as_of='1.0')
    field = exported(Reference(schema=IPublishedTooLate))


class IPublishedEarly(Interface):
    export_as_webservice_entry(as_of='1.0')


class IPublishedLate(Interface):
    export_as_webservice_entry(as_of='2.0')
    field = exported(Reference(schema=IPublishedEarly))


class IPublishedAndThenRemoved(Interface):
    export_as_webservice_entry(
        as_of='1.0', versioned_annotations=[
            VersionedObject('2.0', dict(exported=False))])

class IReferencesPublishedAndThenRemoved(Interface):
    export_as_webservice_entry(as_of='1.0')
    field = exported(Reference(schema=IPublishedAndThenRemoved))


class TestSanityChecking(TestCaseWithWebServiceFixtures):
    """Test lazr.restful's sanity checking upon web service registration."""

    def _test_fails_sanity_check(
        self, expect_failure_in_version, expect_failure_for_reason,
        expect_failure_due_to_interface, *classes):
        """Verify that the given interfaces can't become a web service.

        The given set of interfaces are expected to fail the sanity
        check because they include an annotation that makes some
        version of the web service reference an entry not defined in
        that version (or at all).

        :param expect_failure_in_version: Which version of the web
           service will fail the sanity check.
        :param expect_failure_for_reason: The reason that will be given
           for failing the sanity check.
        :param expect_failure_due_to_interface: The interface that will
           cause the failure due to not being published in
           `expect_failure_in_version`.
        :param classes: The interfaces to attempt to publish as a web
            service. `expect_failure_due_to_interface` will be added to
            this list, so there's no need to specify it again.
        """
        exception = self.assertRaises(
            ValueError, register_test_module,
            'testmod', *(list(classes) + [expect_failure_due_to_interface]))
        expected_message = (
            "In version %(version)s, %(reason)s, but version %(version)s "
            "of the web service does not publish %(interface)s as an entry. "
             "(It may not be published at all.)" % dict(
                version=expect_failure_in_version,
                reason=expect_failure_for_reason,
                interface=expect_failure_due_to_interface.__name__))
        self.assertEquals(str(exception), expected_message)


    def test_reference_to_unpublished_object_fails(self):
        self._test_fails_sanity_check(
            '1.0',
            ("IReferencesNotPublishedEntry_1_0.field is INotPublished"),
            INotPublished, IReferencesNotPublished)

    def test_reference_to_object_published_later_fails(self):
        self._test_fails_sanity_check(
            '1.0',
            ("IReferencesPublishedTooLateEntry_1_0.field is "
             "IPublishedTooLate"),
            IPublishedTooLate, IReferencesPublishedTooLate)

    def test_reference_to_object_published_and_then_removed_fails(self):
        # This setup is acceptable in version 1.0, but in version 2.0
        # IPublishedAndThenRemoved is gone. This puts
        # IReferencesPublishedAndThenRemoved in violation of the
        # sanity check in 2.0, even though it hasn't changed since 1.0.
        self._test_fails_sanity_check(
            '2.0',
            ("IReferencesPublishedAndThenRemovedEntry_2_0.field is "
             "IPublishedAndThenRemoved"),
            IPublishedAndThenRemoved, IReferencesPublishedAndThenRemoved)

    def test_reference_to_object_published_earlier_succeeds(self):
        # It's okay for an object defined in 2.0 to reference an
        # object first defined in 1.0, so long as the referenced
        # object is also present in 2.0.

        # We'll call this test a success if it doesn't raise an exception.
        module = register_test_module(
            'testmod', IPublishedEarly, IPublishedLate)

    # At this point we've tested all the ways entries might not be
    # published in a given version: they might never be published,
    # they might be published later, or they might be published
    # earlier and then removed.

    # Now we need to test all the places an unpublished entry might
    # show up, not counting 'as the referent of a Reference field',
    # which we've already tested.

    def test_reference_to_collection_of_unpublished_objects_fails(self):
        # An entry may define a field that's a scoped collection of
        # unpublished entries.
        self._test_fails_sanity_check(
            '1.0',
            ("IReferencesCollectionOfNotPublishedEntry_1_0.field is a "
             "collection of INotPublished"),
            INotPublished, IReferencesCollectionOfNotPublished)

    def test_operation_returning_unpublished_object_fails(self):
        # An operation may return an unpublished entry.
        self._test_fails_sanity_check(
            '1.0',
            ("named operation get_impossible_object returns INotPublished"),
            INotPublished, IOperationReturnsNotPublished)

    def test_operation_returning_collection_of_unpublished_object_fails(self):
        # An operation may return a collection of unpublished entries.
        self._test_fails_sanity_check(
            '1.0',
            ("named operation get_impossible_objects returns a collection "
             "of INotPublished"),
            INotPublished, IOperationReturnsNotPublishedCollection)

    def test_operation_taking_unpublished_argument_fails(self):
        # An operation may take an unpublished entry as an argument.
        self._test_fails_sanity_check(
            '1.0',
            ("named operation use_impossible_object accepts INotPublished"),
            INotPublished, IOperationAcceptsNotPublished)

    def test_operation_taking_unpublished_collection_argument_fails(self):
        # An operation may take a collection of unpublished entries as
        # an argument.
        self._test_fails_sanity_check(
            '1.0',
            ("named operation use_impossible_objects accepts a collection "
             "of INotPublished"),
            INotPublished, IOperationAcceptsCollectionOfNotPublished)

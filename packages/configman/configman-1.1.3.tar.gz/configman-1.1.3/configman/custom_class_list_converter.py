from configman import RequiredConfig, Namespace, ConfigurationManager
from configman.converters import class_converter, py_obj_to_str

#------------------------------------------------------------------------------
def _default_list_splitter(class_list_str):
    return [x.strip() for x in class_list_str.split(',')]

#------------------------------------------------------------------------------
def _default_class_extractor(list_element):
    return list_element

#------------------------------------------------------------------------------
def _default_extra_extractor(list_element):
    raise NotImplementedError()

#------------------------------------------------------------------------------
def _default_to_string_converter(inner_class_instance):
    return inner_class_instance.original_input


#------------------------------------------------------------------------------
def classes_in_namespaces_converter_with_compression(
      reference_namespace={},
      template_for_namespace="class-%(name)s",
      list_splitter_fn=_default_list_splitter,
      class_extractor=_default_class_extractor,
      extra_extractor=_default_extra_extractor,
      to_str_converter=_default_to_string_converter
    ):
    """
    parameters:
        template_for_namespace - a template for the names of the namespaces
                                 that will contain the classes and their
                                 associated required config options.  There are
                                 two template variables available: %(name)s -
                                 the name of the class to be contained in the
                                 namespace; %(index)d - the sequential index
                                 number of the namespace.
        list_converter - a function that will take the string list of classes
                         and break it up into a sequence if individual elements
        class_extractor - a function that will return the string version of
                          a classname from the result of the list_converter
        extra_extractor - a function that will return a Namespace of options
                          created from any extra information associated with
                          the classes returned by the list_converter function
                              """

    #--------------------------------------------------------------------------
    def class_list_converter(class_list_str):
        """This function becomes the actual converter used by configman to
        take a string and convert it into the nested sequence of Namespaces,
        one for each class in the list.  It does this by creating a proxy
        class stuffed with its own 'required_config' that's dynamically
        generated."""
        if isinstance(class_list_str, basestring):
            class_str_list = list_splitter_fn(class_list_str)
        else:
            raise TypeError('must be derivative of a basestring')

        #======================================================================
        class InnerClassList(RequiredConfig):
            """This nested class is a proxy list for the classes.  It collects
            all the config requirements for the listed classes and places them
            each into their own Namespace.
            """
            # we're dynamically creating a class here.  The following block of
            # code is actually adding class level attributes to this new class
            required_config = Namespace()  # 1st requirement for configman
            subordinate_namespace_names = []  # to help the programmer know
                                              # what Namespaces we added
            namespace_template = template_for_namespace  # save the template
                                                         # for future reference
            original_input = class_list_str.replace('\n', '\\n') # for display
            # for each class in the class list
            class_dict = {}
            for namespace_index, class_list_element in enumerate(
                                                               class_str_list):
                a_class = class_converter(class_extractor(class_list_element))
                class_dict[a_class.__name__] = a_class
                # figure out the Namespace name
                namespace_name_dict = {'name': a_class.__name__,
                                       'index': namespace_index}
                namespace_name = template_for_namespace % namespace_name_dict
                subordinate_namespace_names.append(namespace_name)
                # create the new Namespace
                required_config.namespace(namespace_name)
                a_class_namespace = required_config[namespace_name]
                # add options for the 'extra data'
                try:
                    extra_options = extra_extractor(class_list_element)
                    a_class_namespace.update(extra_options)
                except NotImplementedError:
                    pass
                # add options frr the classes required config
                try:
                    for k, v in a_class.get_required_config().iteritems():
                        if k not in reference_namespace:
                            a_class_namespace[k] = v
                except AttributeError: # a_class has no get_required_config
                    pass

            #to_str = to_str_converter
            @classmethod
            def to_str(cls):
                """this method takes this inner class object and turns it back
                into the original string of classnames.  This is used
                primarily as for the output of the 'help' option"""
                return cls.original_input
                #return ', '.join(
                    #py_obj_to_str(v[name_of_class_option].value)
                        #for v in cls.get_required_config().values()
                        #if isinstance(v, Namespace))

        return InnerClassList  # result of class_list_converter
    return class_list_converter  # result of classes_in_namespaces_converter


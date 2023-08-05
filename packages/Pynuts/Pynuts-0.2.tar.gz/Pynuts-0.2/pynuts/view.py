"""View file for Pynuts."""

import flask
import jinja2
from flask_wtf import Form, TextField
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage

from sqlalchemy.orm import class_mapper
from sqlalchemy.util import classproperty
from sqlalchemy.orm.attributes import InstrumentedAttribute


class FormBase(Form):

    def handle_errors(self):
        """Flash all the form errors."""
        if self.errors:
            for key, errors in self.errors.items():
                flask.flash(jinja2.Markup(
                    u'<label for="%s">%s</label>: %s.' % (
                        key, self[key].label.text, ', '.join(errors))),
                    'error')


class MetaView(type):
    """Metaclass for view classes."""
    def __init__(mcs, name, bases, dict_):
        if mcs.model:
            # TODO: find a better name than the name of the class
            mcs._pynuts.views[mcs.__name__] = mcs
            mcs._mapping = mcs._mapping or class_mapper(mcs.model)
            column_names = [column.key for column in mcs._mapping.columns]
            mcs.list_columns = (mcs.list_column or column_names[0],)
            mcs.table_columns = mcs.table_columns or column_names
            mcs.create_columns = mcs.create_columns or column_names
            mcs.read_columns = mcs.read_columns or column_names
            mcs.update_columns = mcs.update_columns or column_names
            if mcs.Form:
                for action in ('list', 'table', 'create', 'read', 'update'):
                    class_name = '%sForm' % action.capitalize()
                    columns = getattr(mcs, '%s_columns' % action)
                    setattr(mcs, class_name, type(
                        class_name, (mcs.form_base_class,), dict(
                            (field_name, getattr(
                                mcs.Form, field_name, TextField(field_name)))
                            for field_name in columns)))
        super(MetaView, mcs).__init__(name, bases, dict_)


class ModelView(object):
    """This class represents the view of a SQLAlchemy model class.

    It grants CRUD (Create, Read, Update, Delete) operations
    and provides a specific view for each of these operations.

    :param keys: Your model primary key(s)
    :type keys: str, tuple

    :param data: Your model data
    :type data: dict

    """

    # Metaclass
    __metaclass__ = MetaView

    # Mapper
    _mapping = None

    #: SQLAlchemy model
    model = None

    form_base_class = FormBase

    Form = None
    """
    WTForms view form. Declare it in your view like this:

    >>> class MyView(ModelView):
    ...     class Form(Form):
    ...         id = IntegerField(u'Id', validators=[Required()])
    ...         name = TextField(u'Last name', validators=[Required()])
    """

    # Endpoints
    create_endpoint = None
    read_endpoint = None
    update_endpoint = None
    delete_endpoint = None
    list_endpoint = None
    table_endpoint = None

    # Templates
    list_template = '_pynuts/list.jinja2'
    table_template = '_pynuts/table.jinja2'
    create_template = '_pynuts/create.jinja2'
    read_template = '_pynuts/read.jinja2'
    update_template = '_pynuts/update.jinja2'
    delete_template = '_pynuts/delete.jinja2'

    #: The column which represents your class
    list_column = None

    #: The columns displayed in the table
    table_columns = None

    #: The column you can set when creating an instance
    create_columns = None

    #: The columns displayed in the view list
    read_columns = None

    #: The columns you can edit
    update_columns = None

    # Properties
    @property
    def primary_keys(self):
        """Primary keys/value dict."""
        return dict(
            (column.key, getattr(self.data, column.key))
            for column in self.mapping.primary_key)

    @property
    def name(self):
        """Common name."""
        return getattr(self.data, self.list_column)

    def __init__(self, keys=None, data=None):
        if keys:
            self.data = self.model.query.get_or_404(keys)
        elif data:
            self.data = data
        else:
            self.data = None

    # @classproperty
    # def list_field(cls):
    #     """Return the list field."""
    #     return cls.ListForm()._fields[cls.list_column]

    @classproperty
    def table_fields(cls):
        """Return the table fields."""
        return cls.TableForm()._fields

    @cached_property
    def create_form(self):
        """Return the create fields."""
        return self.CreateForm()

    @cached_property
    def read_fields(self):
        """Return the read fields."""
        return self.ReadForm(obj=self.data)

    @cached_property
    def update_form(self):
        """Return the update fields."""
        return self.UpdateForm(obj=self.data)

    @classproperty
    def mapping(cls):
        """Table mapping."""
        return cls._mapping

    @classproperty
    def session(cls):
        """Database session."""
        return cls.model.query.session

    @classmethod
    def query(cls, query=None, elements=None):
        """Return all the model elements according to a query..

        :param query: The SQLAlchemy query
        :type query: str
        :param elements: A model list (if present, does not execute query)
        :type elements: list

        """
        if elements is not None:
            iterable = elements
        elif query:
            iterable = query.all()
        else:
            iterable = cls.model.query
            if hasattr(cls, 'order_by'):
                iterable = iterable.order_by(cls.order_by)
            iterable = iterable.all()

        for data in iterable:
            yield cls(data=data)

    @classmethod
    def _get_form_attributes(cls, form):
        """Return the form attributes which are defined on the model."""
        result = {}
        for key in form:
            model_attr = getattr(cls.model, key.name, None)
            if model_attr is not None:
                if (isinstance(model_attr, InstrumentedAttribute) or
                    isinstance(model_attr, property) and model_attr.fset is not
                        None):
                    result[key.name] = key.data
        return result

    @classmethod
    def handle_errors(cls, form):
        """Flash all the errors contained in the form."""
        # Test for attribute if the form has not "handle_errors" method.
        form.handle_errors()

    def template_url_for(self, endpoint, **kwargs):
        """Return endpoint if callable, url_for this endpoint else.

        If the given endpoint is already an url, return as is.

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: str, func(lambda)

        """
        if callable(endpoint):
            dict_args = dict(self.primary_keys)
            dict_args.update(kwargs)
            return endpoint(self, **dict_args)
        elif endpoint:
            if '/' in endpoint:
                return endpoint
            else:
                return flask.url_for(endpoint, **kwargs)

    def action_url_for(self, action, **kwargs):
        """Return url_for for CRUD operation.

        :param action: Endpoint name
        :type action: str

        """
        return self.template_url_for(
            getattr(type(self), '%s_endpoint' % action), **kwargs)

    # Endpoints methods
    @classmethod
    def create_page(cls, function):
        """ Set the create_endpoint class property according
            to the function name.
        """
        check_auth = getattr(function, '_auth_fun', lambda: True)
        cls.create_endpoint = classproperty(
            lambda cls: check_auth() and function.__name__)
        return function

    @classmethod
    def read_page(cls, function):
        """ Set the read_endpoint class property according
            to the function name.
        """
        check_auth = getattr(function, '_auth_fun', lambda: True)
        cls.read_endpoint = classproperty(
            lambda cls: check_auth() and (
                lambda cls, **primary_keys:
                flask.url_for(function.__name__, **primary_keys)))
        return function

    @classmethod
    def update_page(cls, function):
        """ Set the update_endpoint class property according
            to the function name.
        """
        check_auth = getattr(function, '_auth_fun', lambda: True)
        cls.update_endpoint = classproperty(
            lambda cls: check_auth() and (
                lambda cls, **primary_keys:
                flask.url_for(function.__name__, **primary_keys)))
        return function

    @classmethod
    def delete_page(cls, function):
        """ Set the delete_endpoint class property according
            to the function name.
        """
        check_auth = getattr(function, '_auth_fun', lambda: True)
        cls.delete_endpoint = classproperty(
            lambda cls: check_auth() and (
                lambda cls, **primary_keys:
                flask.url_for(function.__name__, **primary_keys)))
        return function

    @classmethod
    def table_page(cls, function):
        """ Set the table_endpoint class property according
            to the function name.
        """
        check_auth = getattr(function, '_auth_fun', lambda: True)
        cls.table_endpoint = classproperty(
            lambda cls: check_auth() and function.__name__)
        return function

    @classmethod
    def list_page(cls, function):
        """ Set the list_endpoint class property according
            to the function name.
        """
        check_auth = getattr(function, '_auth_fun', lambda: True)
        cls.list_endpoint = classproperty(
            lambda cls: check_auth() and function.__name__)
        return function

    # View methods
    @classmethod
    def view_list(cls, query=None, endpoint=None, no_result_message=None,
                  elements=None, **kwargs):
        """Render the HTML for list_template.

        :param query: The SQLAlchemy query used for rendering the list
        :type query: str
        :param no_result_message: The message displayed if no result
                                  is returned by the query
        :type no_result_message: str
        :param elements: A model list replacing query
        :type elements: list

        """
        template = cls.environment.get_template(cls.list_template)
        return jinja2.Markup(template.render(
            views=cls.query(query, elements), endpoint=endpoint,
            view_class=cls, no_result_message=no_result_message, **kwargs))

    @classmethod
    def view_table(cls, query=None, endpoint=None, no_result_message=None,
                   elements=None, actions=None, no_default_actions=False,
                   **kwargs):
        """Render the HTML for table_template.

        :param query: The SQLAlchemy query used for rendering the table
        :type query: str
        :param no_result_message: The message displayed if not any result
                                  is returned by the query
        :type no_result_message: str
        :param elements: A model list replacing query
        :type elements: list

        """
        template = cls.environment.get_template(cls.table_template)
        return jinja2.Markup(template.render(
            views=cls.query(query, elements), endpoint=endpoint,
            view_class=cls, no_result_message=no_result_message,
            actions=actions or [], no_default_actions=no_default_actions,
            **kwargs))

    def view_create(self, action=None, **kwargs):
        """Render the HTML for create_template.

        :param action: the URL for the create form validation.

        """
        template = self.environment.get_template(self.create_template)
        return jinja2.Markup(template.render(view=self, action=action,
            **kwargs))

    def view_read(self, **kwargs):
        """Render the HTML for read_template."""
        template = self.environment.get_template(self.read_template)
        return jinja2.Markup(template.render(view=self, **kwargs))

    def view_update(self, action=None, **kwargs):
        """Render the HTML for update_template.

        :param action: the URL for the update form validation.

        """
        template = self.environment.get_template(self.update_template)
        return jinja2.Markup(template.render(view=self, action=action,
            **kwargs))

    def view_delete(self, **kwargs):
        """Render the HTML for delete_template."""
        template = self.environment.get_template(self.delete_template)
        return jinja2.Markup(template.render(view=self, **kwargs))

    # CRUD methods
    @classmethod
    def list(cls, template=None, query=None, **kwargs):
        """Return the list_template.

        :param template: The template you want to render
        :type template: str

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: str, func(lambda)

        """
        return flask.render_template(
            template, view_class=cls, query=query, **kwargs)

    @classmethod
    def table(cls, template=None, query=None, **kwargs):
        """Return the table_template.

        :param template: The template you want to render
        :type template: str

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: str, func(lambda)

        """
        return flask.render_template(
            template, view_class=cls, query=query, **kwargs)

    def render(self, template, **kwargs):
        """Render a template with the view, view_class and instance variables.

        :param template: The template to render
        :type template: str

        """
        return flask.render_template(
            template, view=self, view_class=type(self), instance=self.data,
            **kwargs)

    def create(self, template=None, redirect=None, values=None, **kwargs):
        """Define the create method. Also check the values in the form: \

        If the values are OK : commit the form with its data; \

        Else : Display the form with errors.

        :param template: The template you want to render
        :type template: str

        :param redirect: The URL where you want to redirect after the function
        :type redirect: str, func(lambda)

        :param values: The values of the object you want to create
        :type values: dict

        """
        if self.handle_create_form(values):
            self.session.commit()
            return flask.redirect(
                self.template_url_for(redirect or type(self).read_endpoint))
        return self.render(template, **kwargs)

    def handle_create_form(self, values=None):
        """Handle the create form operation.

        If the field value is a ``FileStorage`` instance
        and has a specified UploadSet, the save operation
        will be performed by this UploadSet.

        If the ``FileStorage`` does not have an associated UploadSet,
        it will look for a save handler method named ``{name}_handler``
        (where ``{name}`` is the field name).

        """
        if self.create_form.validate_on_submit():
            form_values = self._get_form_attributes(self.create_form)
            if values:
                form_values.update(values)
            self.data = self.model(**form_values)

            for key, value in form_values.items():
                if isinstance(value, FileStorage):
                    if hasattr(self.create_form._fields[key], 'upload_set'):
                        handler = self.create_form._fields[key].upload_set
                        if not handler:
                            raise RuntimeError('No UploadSet handler could be'
                                'found for %s' % (key))
                    else:
                        handler = getattr(self, key + '_handler', None)
                        if not handler:
                            raise ValueError(
                                'You must define a %s_handler '
                                'property on your view set to an UploadSet' % key)
                    if value.filename:
                        setattr(self.data, key, handler.save(value))
                    else:
                        setattr(self.data, key, None)

            self.session.add(self.data)
        self.handle_errors(self.create_form)
        return self.data

    def update(self, template=None, redirect=None, **kwargs):
        """Return the update_template. See the create method for more details.

        :param template: The template you want to render
        :type template: str

        :param redirect: The URL where you want to redirect after the function
        :type redirect: str, func(lambda)

        """
        if self.handle_update_form():
            self.session.commit()
            return flask.redirect(
                self.template_url_for(redirect or type(self).read_endpoint))
        return self.render(template, **kwargs)

    def handle_update_form(self):
        """Handle the update form operation.

        If the field value is a ``FileStorage`` instance
        and has a specified UploadSet, the save operation
        will be performed by this UploadSet.

        If the ``FileStorage`` does not have an associated UploadSet,
        it will look for a save handler method named ``{name}_handler``
        (where ``{name}`` is the field name).

        """
        if self.update_form.validate_on_submit():
            for key, value in self._get_form_attributes(
                    self.update_form).items():
                if isinstance(value, FileStorage):
                    if hasattr(self.create_form._fields[key], 'upload_set'):
                        handler = self.create_form._fields[key].upload_set
                        if not handler:
                            raise RuntimeError('No UploadSet handler could be'
                                'found for %s' % (key))
                    else:
                        handler = getattr(self, key + '_handler', None)
                        if not handler:
                            raise ValueError(
                                'You must define a %s_handler '
                                'property on your view set to an UploadSet' % key)
                    if value.filename:
                        setattr(self.data, key, handler.save(value))

                else:
                    setattr(self.data, key, value)
            return True
        self.handle_errors(self.update_form)
        return False

    def read(self, template=None, **kwargs):
        """Return the view_template.

        :param template: The template you want to render
        :type template: str

        """
        self.read_fields.process(obj=self.data)
        return flask.render_template(
            template, view=self, view_class=type(self), instance=self.data,
            **kwargs)

    def delete(self, template=None, redirect=None, **kwargs):
        """Delete an entry from the database.

        :param template: The template you want to render
        :type template: str

        :param redirect: The URL where you want to redirect after the function
        :type redirect: str, func(lambda)

        """
        if flask.request.method == 'POST':
            self.session.delete(self.data)
            self.session.commit()
            return flask.redirect(
                self.template_url_for(
                    redirect or type(self).list_endpoint or
                    type(self).table_endpoint))
        return flask.render_template(
            template, view=self, view_class=type(self), instance=self.data,
            **kwargs)

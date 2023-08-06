# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import select_template
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.views.generic.detail import DetailView, SingleObjectMixin,\
    BaseDetailView

from braces.views import LoginRequiredMixin, PermissionRequiredMixin,\
    MultiplePermissionsRequiredMixin

from files import get_form
from files.models import Attachment


class NextMixin(object):
    """
    A mixin which returns the first valid value from
    either "next" from POST data or success_url. If neither
    is available, try to get the absolute url from model.
    """
    def get_success_url(self):
        url = self.request.POST.get("next", None) or self.success_url
        if not url:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured("No URL to redirect to. Provide a next value, success_url"
                                           " or a get_absolute_url method on the Model.")
        return url


class AttachmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, NextMixin, CreateView):
    """
    View responsible for creating new attachments.
    """
    model = Attachment
    context_object_name = "attachment"
    form_class = get_form()
    template_name = "attachments/form.html"
    permission_required = "files.add_attachment"
    
    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        try:
            data = kwargs["data"]
            ctype_pk, object_pk = data.get("content_type"), data.get("object_id")
            if ctype_pk is None or object_pk is None:
                raise AttributeError("Missing content_type or object_id field.")
            model = ContentType.objects.get_for_id(ctype_pk)
            target = model.get_object_for_this_type(pk=object_pk)
        except AttributeError:
            raise AttributeError("The given content-type id %d does not resolve to a model." % ctype_pk)
        except ContentType.DoesNotExist:
            raise ContentType.DoesNotExist("No matching content-type id and object id exists." % (ctype_pk, object_pk))
        except (ValueError, ValidationError), e:
            raise e("Attempting to get content-type %d and object %d raised %s",
                    (ctype_pk, object_pk, e.__class__.__name__))
        except Exception, e:
            raise e
        return form_class(target, **kwargs)
    
    def form_valid(self, form):
        # Set some additional attributes from request.
        form.instance.creator = self.request.user
        form.instance.ip_address = self.request.META["REMOTE_ADDR"]
        return super(AttachmentCreateView, self).form_valid(form)
    

class AttachmentEditView(LoginRequiredMixin, MultiplePermissionsRequiredMixin, NextMixin, UpdateView):
    """
    Updates an existing attachment with new data.
    """
    model = Attachment
    context_object_name = "attachment"
    form_class = get_form()
    permissions = {
        "any": ("files.change_attachment", "files.can_moderate")
    }
    raise_exception = True  # If user is not allowed to edit the attachment,
                            # return a HttpResponseForbidden response
    
    def get_form(self, form_class):
        obj = self.object.content_type \
            .get_object_for_this_type(pk=self.object.object_id)
        return form_class(obj, **self.get_form_kwargs())

    def get_template_names(self):
        names = super(AttachmentEditView, self).get_template_names()
        if self.object:
            ctype = self.object.content_type
            template_search_list = [
                "attachments/%s/%s/edit_form.html" % (ctype.app_label, ctype.model),
                "attachments/%s/edit_form.html" % ctype.app_label,
                "attachments/%s/edit_form.html" % ctype.model,
                "attachments/edit_form.html"
            ]
            names = template_search_list + names
        return names


class AttachmentDetailView(DetailView):
    """
    Returns the details of an attachment.
    """
    model = Attachment
    context_object_name = "attachment"
    template_name = "attachments/view.html"
    

class AttachmentDeleteView(LoginRequiredMixin, MultiplePermissionsRequiredMixin, NextMixin, DeleteView):
    """
    Deletes an attachment from the storage backend.
    """
    model = Attachment
    context_object_name = "attachment"
    permissions = {
        "all": ("files.delete_attachment",)
    }
    raise_exception = True  # If user is not allowed to delete the attachment,
                            # return a HttpResponseForbidden response
    
    def dispatch(self, request, *args, **kwargs):
        self.kwargs = kwargs
        obj = self.get_object()
        if not request.user == obj.creator:
            # If attachment is not created by the user who tries
            # to delete it, the user need to have the "delete_all_attachment"
            # permission.
            self.permissions["all"] = ("files.delete_attachment", "files.delete_all_attachment")
        return super(AttachmentDeleteView, self).dispatch(request, *args, **kwargs)
    
    def get_template_names(self):
        """
        Add content type object app_name and model
        to template search path.
        """
        names = super(AttachmentDeleteView, self).get_template_names()
        if self.object:
            ctype = self.object.content_type
            template_search_list = [
                "attachments/%s/%s/delete.html" % (ctype.app_label, ctype.model),
                "attachments/%s/delete.html" % ctype.app_label,
                "attachments/%s/delete.html" % ctype.model,
                "attachments/delete.html"
            ]
            names = template_search_list + names
        return names
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        next_url = self.get_success_url()

        # Redirect to "next" from POST data, or success_url.
        # If neither is present, render a default response
        # using a custom or default template.
        if next_url:
            return HttpResponseRedirect(next_url)
        else:
            ctype = self.object.content_type
            template_search_list = [
                "attachments/%s/%s/deleted.html" % (ctype.app_label, ctype.model),
                "attachments/%s/deleted.html" % ctype.app_label,
                "attachments/%s/deleted.html" % ctype.model,
                "attachments/deleted.html"
            ]
            template = select_template(template_search_list)
            return render_to_response(template.name, self.get_context_data(), RequestContext(request))
    
    
class AttachmentDownloadView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView, SingleObjectMixin):
    """
    Returns the attachment file as a HttpResponse.
    """
    model = Attachment
    context_object_name = "attachment"
    require_auth = getattr(settings, "REQUIRE_AUTH_DOWNLOAD", False)
    raise_exception = True  # If user is not allowed to download the file,
                            # return a HttpResponseForbidden response
    
    def dispatch(self, request, *args, **kwargs):
        if self.require_auth is True:
            # Set permission_required, and call the
            # mixin dispatch methods
            self.permission_required = "files.download_attachment"
            return super(AttachmentDownloadView, self).dispatch(request, *args, **kwargs)
        else:
            # Call the normal dispatch method
            return super(BaseDetailView, self).dispatch(request, *args, **kwargs)
    
    def render_to_response(self, context):
        obj = context["attachment"]
        response = HttpResponse(obj.attachment.file.read(), mimetype=obj.mimetype)
        response["Content-Disposition"] = "inline; filename=%s" % obj.filename
        return response

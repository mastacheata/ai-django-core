from django.shortcuts import render


class _FormsetMixin:
    """
    Mixin for handling a django form with with a formset. Extends the form handling logic to handle a formset object.

    Attention: Do NOT use directly. Do use FormsetUpdateViewMixin or FormsetCreateViewMixin
    """

    formset_class = None
    object = None

    def get_formset_kwargs(self):
        # may be overridden or extended
        return dict(instance=self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.formset_class(**self.get_formset_kwargs())
        return context

    def form_valid(self, form, formset):
        # Updates `self.object` internally and returns a redirect response instance
        response = super().form_valid(form=form)

        # Update formset
        formset.instance = self.object
        formset.save()

        if hasattr(self, 'additional_is_valid'):
            self.additional_is_valid(form, formset)

        # Return response (a redirect)
        return response

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(**self.get_form_kwargs())
        formset = self.formset_class(request.POST, request.FILES, **self.get_formset_kwargs())

        # Form and formset valid?
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form=form, formset=formset)

        # Get all context data
        context = self.get_context_data()

        # Update form and formset variables
        context['form'] = form
        context['formset'] = formset

        # Pass all data to template
        return render(request, self.get_template_names(), context)


class FormsetUpdateViewMixin(_FormsetMixin):
    """
    Can be used to validate and save a formset.
    Usage is similar to regular UpdateView:

    class MandantSettingsUpdate(FormsetUpdateViewMixin, generic.UpdateView):
        form_class = MandantSettingsForm
        template_name = 'mandant/mandantsettings_form.html'
        formset_class = inlineformset_factory(Mandant, MandantProdukttyp, form=MandantProdukttypForm, extra=0, \
                                              can_delete=False)
        model = Mandant
        success_url = reverse_lazy('mandant:edit-settings')

        def additional_is_valid(self, form, formset):
            messages.add_message(self.request, messages.INFO, 'Einstellungen wurden erfolgreich aktualisiert.')

    """

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class FormsetCreateViewMixin(_FormsetMixin):
    """
    Can be used to validate and save a formset.
    Usage is similar to regular CreateView. See FormsetUpdateViewMixin.
    """

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)

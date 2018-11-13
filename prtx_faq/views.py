from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DeleteView, FormView, UpdateView, TemplateView

from prtx_faq.models import FAQ, FAQCategory
from prtx_faq.forms import FAQCategoryForm, FAQForm
from prtx_faq.prtx import PRTX


class FAQView(TemplateView):  # TODO
    template_name = 'prtx_faq/faq.{}.html'.format(PRTX)


class FAQList(ListView):
    model = FAQ
    context_object_name = 'questions'
    template_name = 'prtx_faq/faq_list.{}.html'.format(PRTX)


class FAQCreate(FormView):  # TODO
    template_name = 'prtx_faq/faq_create.{}.html'.format(PRTX)
    form_class = FAQForm

    def get_success_url(self):
        kwargs = {'event': self.request.event.slug}
        if PRTX == 'pretix':
            kwargs['organizer'] = self.request.organizer.slug
        messages.success(self.request, _('Category created!'))
        return reverse('plugins:prtx_faq:faq.list', kwargs=kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.request.event
        return kwargs


class FAQEdit(UpdateView):  # TODO
    model = FAQ
    template_name = 'prtx_faq/faq_edit.{}.html'.format(PRTX)


class FAQDelete(DeleteView):  # TODO
    model = FAQ
    template_name = 'prtx_faq/faq_delete.{}.html'.format(PRTX)


def faq_move(request, pk, up=True):
    try:
        question = FAQ.objects.get(category__event=request.event, pk=pk)
    except FAQ.DoesNotExist:
        raise Http404(_('The selected question does not exist.'))
    questions = list(FAQ.objects.filter(category=question.category).order_by('position'))

    index = questions.index(question)
    if index != 0 and up:
        questions[index - 1], questions[index] = questions[index], questions[index - 1]
    elif index != len(questions) - 1 and not up:
        questions[index + 1], questions[index] = questions[index], questions[index + 1]

    for i, qst in enumerate(questions):
        if qst.position != i:
            qst.position = i
            qst.save()
    messages.success(request, _('The order of questions has been updated.'))
    kwargs = {'event': request.event.slug}
    if PRTX == 'pretix':
        kwargs['organizer'] = request.organizer.slug
    return reverse('plugins:prtx_faq:faq.list', kwargs=kwargs)


def faq_up(request, **kwargs):
    return redirect(faq_move(request, kwargs.get('pk'), up=True))


def faq_down(request, **kwargs):
    return redirect(faq_move(request, kwargs.get('pk'), up=False))


class FAQCategoryList(ListView):
    model = FAQCategory
    context_object_name = 'categories'
    template_name = 'prtx_faq/faq_category_list.{}.html'.format(PRTX)


class FAQCategoryCreate(FormView):
    template_name = 'prtx_faq/faq_category_create.{}.html'.format(PRTX)
    form_class = FAQCategoryForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        kwargs = {'event': self.request.event.slug}
        if PRTX == 'pretix':
            kwargs['organizer'] = self.request.organizer.slug
        messages.success(self.request, _('Category created!'))
        return reverse('plugins:prtx_faq:faq.category.list', kwargs=kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.request.event
        return kwargs


class FAQCategoryEdit(UpdateView):  # TODO
    model = FAQCategory
    template_name = 'prtx_faq/faq_category_edit.{}.html'.format(PRTX)


class FAQCategoryDelete(DeleteView):  # TODO
    model = FAQCategory
    template_name = 'prtx_faq/faq_category_delete.{}.html'.format(PRTX)


def faq_category_move(request, pk, up=True):
    try:
        category = request.event.faq_categories.get(pk=pk)
    except FAQCategory.DoesNotExist:
        raise Http404(_('The selected category does not exist.'))
    categories = list(request.event.faq_categories.order_by('position'))

    index = categories.index(category)
    if index != 0 and up:
        categories[index - 1], categories[index] = categories[index], categories[index - 1]
    elif index != len(categories) - 1 and not up:
        categories[index + 1], categories[index] = categories[index], categories[index + 1]

    for i, cat in enumerate(categories):
        if cat.position != i:
            cat.position = i
            cat.save()
    messages.success(request, _('The order of categories has been updated.'))
    kwargs = {'event': request.event.slug}
    if PRTX == 'pretix':
        kwargs['organizer'] = request.organizer.slug
    return reverse('plugins:prtx_faq:faq.category.list', kwargs=kwargs)


def faq_category_up(request, **kwargs):
    return redirect(faq_category_move(request, kwargs.get('pk'), up=True))


def faq_category_down(request, **kwargs):
    return redirect(faq_category_move(request, kwargs.get('pk'), up=False))

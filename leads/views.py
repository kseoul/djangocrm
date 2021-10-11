from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, ListView, FormView
from django.views.generic.edit import DeleteView
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from agents.mixins import OrganizerAndLoginRequiredMixin

from .models import Category, Lead, Agent
from .forms import AssignAgentForm, LeadForm,LeadModelForm,CustomUserCreationForm,LeadCategoryUpdateForm


# Create your views here

class LandingPageView(TemplateView):
    template_name = "landing.html"

class LeadListView(LoginRequiredMixin, ListView):
    template_name="leads/lead_list.html"
    context_object_name="leads"
    
    def get_queryset(self):
        user = self.request.user

        # Initial queryset of leads for the entire organization
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile,
                agent__isnull=False
            )
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization, 
                agent__isnull=False
            )
            # filter leads for current agent
            queryset = queryset.filter(agent__user=user)
        return queryset
    
    def get_context_data(self, **kwargs):
        user = self.request.user

        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile,
                agent__isnull=True
            )
            context.update({
                "unassigned_leads": queryset
            })
        
        return context

class LeadCreateView(OrganizerAndLoginRequiredMixin, CreateView):
    template_name="leads/lead_create.html"
    form_class=LeadModelForm
    
    def get_success_url(self) -> str:
        return reverse("leads:lead-list")

    def form_valid(self, form):
        #send mail
        send_mail(
            subject="A lead has been created",
            message="Go to site to see the new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        return super(LeadCreateView,self).form_valid(form)
    

class LeadDetailView(OrganizerAndLoginRequiredMixin, DetailView):
    template_name="leads/lead_detail.html"
    queryset = Lead.objects.all()
    def get_queryset(self):
        user = self.request.user

        # Initial queryset of leads for the entire organization
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            # filter leads for current agent
            queryset = queryset.filter(agent__user=user)
        return queryset

class LeadUpdateView(OrganizerAndLoginRequiredMixin, UpdateView):
    template_name="leads/lead_update.html"
    form_class = LeadModelForm
    
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")

class LeadDeleteView(OrganizerAndLoginRequiredMixin, DeleteView):
    template_name="leads/lead_delete.html"
    
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")

class SignupView(CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self) -> str:
        return reverse("login")
    pass

class AssignAgentView(OrganizerAndLoginRequiredMixin, FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)

    
class CategoryListView(LoginRequiredMixin, ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"
    
    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile
            )
        else:
            queryset = Lead.objects.filter(
                organization = user.agent.organization
            )
        context.update({
            "unassigned_lead_count":queryset.filter(category__isnull=True).count()
        })
        return context
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization
            )
        return queryset

class CategoryDetailView(LoginRequiredMixin, DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        leads = self.get_object().leads.all()
        context.update({
            "leads":leads
        })
        return context

    def get_queryset(self):
        user = self.request.user

        # Initial queryset of leads for the entire organization
        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization
            )
        return queryset    

class LeadCategoryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        print(self.get_object())
        return reverse("leads:lead-detail", kwargs={"pk":self.get_object().id})

'''
#def landing_page(request):
#    return render(request, "landing.html")

def lead_list(request):
    leads = Lead.objects.all()
    context = {
        "leads":leads
    }
    return render(request, "leads/lead_list.html", context)

def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        "lead":lead
    }
    return render(request,"leads/lead_detail.html",context)

def lead_create(request):
    if request.method == "POST":
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/leads')
    context = {
        "form": LeadModelForm()
    }
    return render(request,"leads/lead_create.html",context)


def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    print(form)
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "form": form,
        "lead": lead
    }
    return render(request, "leads/lead_update.html",context)

def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")

def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadForm()
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            age = form.cleaned_data['age']
            lead.first_name = first_name
            lead.last_name = last_name
            lead.age = age
            lead.save()
            return redirect("/leads")
    context = {
        "form": form,
        "lead": lead
    }
    return render(request, "./lead_update.html", context)



from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Lead, Agent
from .forms import LeadForm,LeadModelForm
# Create your views here.

def lead_list(request):
    leads = Lead.objects.all()
    context = {
        "leads":leads
    }
    return render(request, "./lead_list.html", context)

def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        "lead":lead
    }
    return render(request,"./lead_detail.html",context)

def lead_create(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            age = form.cleaned_data['age']
            agent = Agent.objects.first()
            Lead.objects.create(
                first_name=first_name,
                last_name=last_name,
                age=age,
                agent=agent
            )
        return redirect('/leads')
    context = {
        "form": LeadModelForm()
    }
    return render(request,"./lead_create.html",context)
'''
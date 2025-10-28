from django.shortcuts import render, redirect
from django.views.generic import View, FormView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.security.form import UserLoginForm, UserRegisterForm


class LoginRegisterView(View):
    """
    Vista que maneja tanto login como registro en la misma página
    """
    template_name = 'security/auth/login.html'
    
    def get(self, request):
        # Si el usuario ya está autenticado, redirigir al dashboard
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        
        # Crear ambos formularios vacíos
        login_form = UserLoginForm()
        register_form = UserRegisterForm()
        
        context = {
            'login_form': login_form,
            'register_form': register_form,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Determinar qué formulario se envió
        if 'login_submit' in request.POST:
            return self.handle_login(request)
        elif 'register_submit' in request.POST:
            return self.handle_register(request)
        
        return redirect('login')
    
    def handle_login(self, request):
        """
        Maneja el proceso de inicio de sesión
        """
        login_form = UserLoginForm(data=request.POST)
        register_form = UserRegisterForm()
        
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            
            # Autenticar al usuario
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.first_name}!')
                
                # Redirigir a la página siguiente o al dashboard
                next_url = request.GET.get('next', 'core:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Credenciales incorrectas. Por favor intenta de nuevo.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
        
        context = {
            'login_form': login_form,
            'register_form': register_form,
            'show_login': True,
        }
        return render(request, self.template_name, context)
    
    def handle_register(self, request):
        """
        Maneja el proceso de registro
        """
        login_form = UserLoginForm()
        register_form = UserRegisterForm(request.POST)
        
        if register_form.is_valid():
            # Guardar el nuevo usuario
            user = register_form.save()
            
            # Autenticar y loguear automáticamente
            username = register_form.cleaned_data.get('username')
            password = register_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Registro exitoso! Bienvenido {user.first_name}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
        
        context = {
            'login_form': login_form,
            'register_form': register_form,
            'show_register': True,
        }
        return render(request, self.template_name, context)


class LogoutView(View):
    """
    Vista para cerrar sesión
    """
    def get(self, request):
        logout(request)
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return redirect('security:login')
    
    def post(self, request):
        logout(request)
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return redirect('security:login')

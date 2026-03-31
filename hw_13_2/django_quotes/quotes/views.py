from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quote, Author
from .forms import AuthorForm, QuoteForm # Убедитесь, что создали файл forms.py

# 1. Главная страница (доступна всем)
def main(request):
    quotes = Quote.objects.all()
    return render(request, 'quotes/main.html', {'quotes': quotes})

# 2. Страница автора (доступна всем)
def author_detail(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    return render(request, 'quotes/author.html', {'author': author})

# 3. Добавление нового автора (только для зарегистрированных)
@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='quotes:root')
        return render(request, 'quotes/add_author.html', {'form': form})
    
    return render(request, 'quotes/add_author.html', {'form': AuthorForm()})

# 4. Добавление новой цитаты (только для зарегистрированных)
@login_required
def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to='quotes:root')
        return render(request, 'quotes/add_quote.html', {'form': form})
    
    return render(request, 'quotes/add_quote.html', {'form': QuoteForm()})
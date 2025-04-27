from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import *
from .forms import RegisterForm, FeedbackForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # DO NOT create a Score here
            send_mail(
                'Welcome to Quiz Platform!',
                'Thank you for registering. Start taking quizzes now!',
                'no-reply@quizplatform.com',
                [user.email],
                fail_silently=False,
            )
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') 
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid form submission')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    scores = Score.objects.filter(user=request.user)
    return render(request, 'profile.html', {
        'user_profile': user_profile, 
        'scores': scores
    })

@login_required
def quiz_home(request):
    return render(request, 'quiz_home.html')

@login_required
def quiz(request, category_id, difficulty_id):
    category = QuizCategory.objects.get(id=category_id)
    difficulty = DifficultyLevel.objects.get(id=difficulty_id)
    questions = Question.objects.filter(category=category, difficulty=difficulty)

    if request.method == 'POST':
        answers = {question.id: request.POST.get(f'question_{question.id}') for question in questions if request.POST.get(f'question_{question.id}')}
        score_value = calculate_score(questions, answers)

        correct_answers = sum(1 for question in questions if answers.get(question.id) == str(question.correct_option))

        # Save score immediately after quiz
        Score.objects.create(user=request.user, category=category, difficulty=difficulty, score=score_value)

        if correct_answers >= 3:
            next_difficulty_id = difficulty_id + 1
            if next_difficulty_id > 3:
                return redirect('results')
            else:
                return redirect('quiz', category_id=category_id, difficulty_id=next_difficulty_id)
        else:
            return render(request, 'quiz.html', {
                'category': category,
                'difficulty': difficulty,
                'questions': questions,
                'message': f"You've only answered {correct_answers} correct answer(s). Please try again."
            })

    return render(request, 'quiz.html', {'category': category, 'difficulty': difficulty, 'questions': questions})

def calculate_score(questions, answers):
    score = 0
    for question in questions:
        user_answer = answers.get(question.id)
        if user_answer and int(user_answer) == question.correct_option:
            score += 1
    return score

@login_required
def results(request):
    total_score = Score.objects.filter(user=request.user).aggregate(total=models.Sum('score'))['total'] or 0
    return render(request, 'results.html', {'score': total_score})


@login_required
def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect('home')
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', {'form': form})

@login_required
def top_scorers(request):
    categories = QuizCategory.objects.all()
    top_scores = {}
    for category in categories:
        top_scores[category.name] = {
            'easy': Score.objects.filter(category=category, difficulty__id=1)
                                .exclude(user__is_superuser=True)
                                .order_by('-score')[:10],
            'medium': Score.objects.filter(category=category, difficulty__id=2)
                                .exclude(user__is_superuser=True)
                                .order_by('-score')[:10],
            'hard': Score.objects.filter(category=category, difficulty__id=3)
                                .exclude(user__is_superuser=True)
                                .order_by('-score')[:10],
        }
    return render(request, 'top_scorers.html', {'top_scores': top_scores})

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('login')

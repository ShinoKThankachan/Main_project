from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import *
import random
from django.contrib import auth
from .forms import RegisterForm, FeedbackForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confpassword = request.POST['confpassword']

        if password != confpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)

            if user.is_superuser:
                return redirect('admin_home')  
            else:
                return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')

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


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = random.randint(100000, 999999)

        request.session['reset_email'] = email
        request.session['otp'] = otp

        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP is {otp}',
            from_email='youremail@example.com',
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, 'OTP has been sent to your email.')
        return redirect('verify_otp')

    return render(request, 'forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if str(request.session.get('otp')) == entered_otp:
            messages.success(request, 'OTP verified. You can now reset your password.')
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'verify_otp.html')


# Password Reset View
def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        email = request.session.get('reset_email')

        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password has been reset. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect('forgot_password')

    return render(request, 'reset_password.html')
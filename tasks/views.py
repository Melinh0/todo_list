from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm
from django.db.models import Avg, F, ExpressionWrapper, DurationField
from django.utils import timezone
from matplotlib import pyplot as plt
import io
import base64

def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

def task_update(request, pk):
    task = Task.objects.get(pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

def task_delete(request, pk):
    task = Task.objects.get(pk=pk)
    task.delete()
    return redirect('task_list')

def task_charts(request):
    task_count = Task.objects.count()
    completed_task_count = Task.objects.filter(completed=True).count()
    avg_time_result = Task.objects.annotate(
            elapsed_time=ExpressionWrapper(
                F('created_at') - timezone.now(), output_field=DurationField()
            )
        ).aggregate(avg_time=Avg('elapsed_time'))
    avg_time = round(avg_time_result['avg_time'].total_seconds() / 3600, 2) if avg_time_result['avg_time'] else 0

    labels = ['Total Tasks', 'Completed Tasks']
    data = [task_count, completed_task_count]

    fig, ax = plt.subplots()
    ax.bar(labels, data)
    ax.set_ylabel('Number of Tasks')
    ax.set_title('Task Data')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png).decode('utf-8')
    plt.close()

    return render(request, 'tasks/task_charts.html', {'task_count': task_count, 'completed_task_count': completed_task_count, 'avg_time': avg_time, 'graphic': graphic})
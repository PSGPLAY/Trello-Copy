import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from django.db.models import Count

from .forms import (
    BoardForm,
    RegisterForm,
    LoginForm,
    BoardListForm,
    TaskForm,
    WorkspaceForm,
)
from .models import Workspace, Board, BoardList, Task


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto create default workspace for new user
            Workspace.objects.create(
                owner=user,
                name=f"{user.username}'s Workspace",
                description="Default workspace for your personal boards and projects."
            )
            login(request, user)
            return redirect('home:home')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home:home')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home:login')


@login_required
def home(request):
    workspaces = Workspace.objects.filter(owner=request.user).prefetch_related('boards')
    
    # Auto create a workspace if user has none
    if not workspaces.exists():
        default_ws = Workspace.objects.create(
            owner=request.user,
            name=f"{request.user.username}'s Workspace",
            description="Default workspace for your boards and projects."
        )
        workspaces = Workspace.objects.filter(owner=request.user).prefetch_related('boards')

    # Calculate some quick stats for the dashboard header
    total_boards = Board.objects.filter(workspace__owner=request.user).count()
    total_tasks = Task.objects.filter(board_list__board__workspace__owner=request.user).count()
    
    workspace_form = WorkspaceForm()
    board_form = BoardForm(user=request.user)

    return render(request, 'home.html', {
        'workspaces': workspaces,
        'total_boards': total_boards,
        'total_tasks': total_tasks,
        'workspace_form': workspace_form,
        'board_form': board_form,
    })


@login_required
@require_POST
def create_workspace(request):
    form = WorkspaceForm(request.POST)
    if form.is_valid():
        workspace = form.save(commit=False)
        workspace.owner = request.user
        workspace.save()
        return redirect('home:workspace_detail', workspace_id=workspace.id)
    return redirect('home:home')


@login_required
def workspace_detail(request, workspace_id):
    workspace = get_object_or_404(Workspace, id=workspace_id, owner=request.user)
    boards = workspace.boards.all().prefetch_related('lists__tasks')
    all_workspaces = Workspace.objects.filter(owner=request.user)

    if request.method == 'POST':
        form = BoardForm(request.POST, user=request.user)
        if form.is_valid():
            board = form.save(commit=False)
            board.workspace = workspace
            board.save()
            return redirect('home:board_detail', board_id=board.id)
    else:
        form = BoardForm(
            initial={'workspace': workspace},
            user=request.user
        )

    return render(request, 'workspace_detail.html', {
        'workspace': workspace,
        'boards': boards,
        'form': form,
        'all_workspaces': all_workspaces,
    })


@login_required
def board_detail(request, board_id):
    # Support viewing public boards or user-owned boards
    board = get_object_or_404(Board, id=board_id)
    is_owner = (board.workspace.owner == request.user)
    
    if not is_owner and board.visibility != 'public':
        return redirect('home:home')

    lists = board.lists.all().prefetch_related('tasks')
    all_workspaces = Workspace.objects.filter(owner=request.user)
    list_form = BoardListForm()
    task_form = TaskForm()

    return render(request, 'board.html', {
        'board': board,
        'lists': lists,
        'is_owner': is_owner,
        'all_workspaces': all_workspaces,
        'list_form': list_form,
        'task_form': task_form,
    })


@login_required
@require_POST
def update_board(request, board_id):
    board = get_object_or_404(Board, id=board_id, workspace__owner=request.user)
    
    name = request.POST.get('name')
    description = request.POST.get('description')
    visibility = request.POST.get('visibility')
    background = request.POST.get('background')

    if name:
        board.name = name.strip()
    if description is not None:
        board.description = description.strip()
    if visibility in ['private', 'workspace', 'public']:
        board.visibility = visibility
    if background:
        board.background = background

    board.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'name': board.name,
            'visibility': board.visibility,
            'background': board.background
        })

    return redirect('home:board_detail', board_id=board.id)


@login_required
@require_POST
def delete_board(request, board_id):
    board = get_object_or_404(Board, id=board_id, workspace__owner=request.user)
    workspace_id = board.workspace.id
    board.delete()
    return redirect('home:workspace_detail', workspace_id=workspace_id)


@login_required
def create_list(request, board_id):
    board = get_object_or_404(Board, id=board_id, workspace__owner=request.user)

    if request.method == 'POST':
        form = BoardListForm(request.POST)
        if form.is_valid():
            board_list = form.save(commit=False)
            board_list.board = board
            last_list = board.lists.order_by('-position').first()
            board_list.position = (last_list.position + 1) if last_list else 0
            board_list.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'list_id': board_list.id,
                    'name': board_list.name,
                    'position': board_list.position
                })

            return redirect('home:board_detail', board_id=board.id)
    else:
        form = BoardListForm()

    return render(request, 'create_list.html', {'form': form, 'board': board})


@login_required
@require_POST
def update_list(request, list_id):
    board_list = get_object_or_404(BoardList, id=list_id, board__workspace__owner=request.user)
    name = request.POST.get('name')
    if name:
        board_list.name = name.strip()
        board_list.save()
        return JsonResponse({'success': True, 'name': board_list.name})
    return HttpResponseBadRequest("Name required")


@login_required
@require_POST
def delete_list(request, list_id):
    board_list = get_object_or_404(BoardList, id=list_id, board__workspace__owner=request.user)
    board_id = board_list.board.id
    board_list.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('home:board_detail', board_id=board_id)


@login_required
def create_task(request, list_id):
    board_list = get_object_or_404(
        BoardList,
        id=list_id,
        board__workspace__owner=request.user
    )
    board = board_list.board

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.board_list = board_list
            last_task = board_list.tasks.order_by('-position').first()
            task.position = (last_task.position + 1) if last_task else 0
            task.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'task': {
                        'id': task.id,
                        'title': task.title,
                        'description': task.description or '',
                        'label_color': task.label_color or 'blue',
                        'due_date': str(task.due_date) if task.due_date else '',
                        'position': task.position
                    }
                })

            return redirect('home:board_detail', board_id=board.id)

    return redirect('home:board_detail', board_id=board.id)


@login_required
@require_POST
def update_task(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        board_list__board__workspace__owner=request.user
    )

    # Check for drag-and-drop position / list move via JSON or POST
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
    else:
        data = request.POST

    target_list_id = data.get('list_id')
    position = data.get('position')
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    label_color = data.get('label_color')

    if target_list_id:
        target_list = get_object_or_404(
            BoardList,
            id=target_list_id,
            board__workspace__owner=request.user
        )
        task.board_list = target_list

    if position is not None:
        try:
            task.position = int(position)
        except ValueError:
            pass

    if title:
        task.title = title.strip()
    if description is not None:
        task.description = description.strip()
    if label_color:
        task.label_color = label_color
    if due_date:
        task.due_date = due_date if due_date != '' else None
    elif due_date == '':
        task.due_date = None

    task.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description or '',
                'label_color': task.label_color,
                'due_date': str(task.due_date) if task.due_date else '',
                'list_id': task.board_list.id,
                'position': task.position
            }
        })

    return redirect('home:board_detail', board_id=task.board_list.board.id)


@login_required
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(
        Task,
        id=task_id,
        board_list__board__workspace__owner=request.user
    )
    board_id = task.board_list.board.id
    task.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('home:board_detail', board_id=board_id)


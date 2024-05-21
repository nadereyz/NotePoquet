function agregarLista(button) {
    var form = button.closest('form');
    var nombre = form.querySelector('.nombreLista').value;
    if (nombre) {
        var ul = form.nextElementSibling;
        var li = document.createElement('li');
        li.textContent = nombre;
        ul.appendChild(li);
        form.querySelector('.nombreLista').value = ''; 
    } else {
        alert('Por favor, ingrese un nombre para la lista.');
    }
}

function addTask() {
    var input = document.getElementById('taskInput');
    var taskList = document.getElementById('taskList');

    if (input.value.trim() !== '') {
        var li = document.createElement('li');
        li.textContent = input.value;
        taskList.appendChild(li);

        input.value = '';
    } else {
        alert('Por favor, ingrese una tarea.');
    }
}

document.getElementById('taskForm').onsubmit = function(event) {
    event.preventDefault();  
    var title = document.getElementById('titleInput').value;
    var description = document.getElementById('descriptionInput').value;

    if (title && description) {
        fetch('/workspace', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'title=' + encodeURIComponent(title) + '&description=' + encodeURIComponent(description)
        })
        .then(response => response.text())
        .then(html => {
            document.getElementById('taskList').innerHTML += '<li>' + title + ': ' + description + '</li>';
        });
    } else {
        alert('Por favor, complete ambos campos.');
    }
};

document.addEventListener('DOMContentLoaded', function() {
    var moveToInProgressButtons = document.querySelectorAll('.move-to-in-progress');
    moveToInProgressButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            var taskId = button.getAttribute('data-task-id');
            moveTaskToInProgress(taskId);
        });
    });
});

function moveTaskToInProgress(taskId) {
    var taskRow = document.getElementById('task_row_' + taskId);
    var inProgressContainer = document.querySelector('#in-progress-body tbody');
    inProgressContainer.appendChild(taskRow);

    fetch('/start_task/' + taskId, {
        method: 'POST',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text();
    })
    .then(data => {
        console.log('Tarea movida a en progreso:', data);
    })
    .catch(error => {
        console.error('Error al mover la tarea:', error);
    });
}


document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        var flashMessages = document.getElementById('flash-messages');
        if (flashMessages && flashMessages.children.length === 0 && getComputedStyle(flashMessages).display !== 'none') {
            flashMessages.style.display = 'none';
        }
    }, 1);
});

function confirmarEliminacion() {
    return confirm('¿Estás seguro de que deseas eliminar esta tarea?');
}




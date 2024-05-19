// Función para agregar una lista
function agregarLista(button) {
    var form = button.closest('form');
    var nombre = form.querySelector('.nombreLista').value;
    if (nombre) {
        var ul = form.nextElementSibling;
        var li = document.createElement('li');
        li.textContent = nombre;
        ul.appendChild(li);
        form.querySelector('.nombreLista').value = ''; // Limpiar el campo de texto
    } else {
        alert('Por favor, ingrese un nombre para la lista.');
    }
}

// Función para agregar una tarea
function addTask() {
    var input = document.getElementById('taskInput');
    var taskList = document.getElementById('taskList');

    if (input.value.trim() !== '') {
        var li = document.createElement('li');
        li.textContent = input.value;
        taskList.appendChild(li);

        // Limpiar el campo de entrada después de agregar la tarea
        input.value = '';
    } else {
        alert('Por favor, ingrese una tarea.');
    }
}

// Manejar el envío del formulario de tarea
document.getElementById('taskForm').onsubmit = function(event) {
    event.preventDefault(); // Evitar la recarga de la página
    var title = document.getElementById('titleInput').value;
    var description = document.getElementById('descriptionInput').value;

    if (title && description) {
        // Enviar los datos al servidor
        fetch('/workspace', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'title=' + encodeURIComponent(title) + '&description=' + encodeURIComponent(description)
        })
        .then(response => response.text())
        .then(html => {
            // Añadir la tarea a la lista sin recargar la página
            document.getElementById('taskList').innerHTML += '<li>' + title + ': ' + description + '</li>';
        });
    } else {
        alert('Por favor, complete ambos campos.');
    }
};

// Manejar el evento de mover tarea a "En progreso"
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

    // Hacer una solicitud AJAX al servidor
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

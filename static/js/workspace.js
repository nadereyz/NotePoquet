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
        alert('Please enter a task.');
    }
}

document.getElementById('taskForm').onsubmit = function(event) {
    event.preventDefault(); // Evitar la recarga de la página
    var title = document.getElementById('titleInput').value;
    var description = document.getElementById('descriptionInput').value;

    if (title && description) {
        // Aquí puedes usar fetch o XMLHttpRequest para enviar los datos al servidor
        fetch('/add_task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'title=' + encodeURIComponent(title) + '&description=' + encodeURIComponent(description)
        })
        .then(response => response.text())
        .then(html => {
            // Puedes elegir actualizar la página o simplemente añadir el elemento a la lista
            document.getElementById('taskList').innerHTML += '<li>' + title + ': ' + description + '</li>';
        });
    } else {
        alert('Please fill in both fields.');
    }
};

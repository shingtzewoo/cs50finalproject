function stop(id) {
    clearInterval(id);
}
function myMove(elem) {
    const check = elem.innerHTML;
    let pos_hor = 0;
    let pos_vert = 0;
    let end = 400;
    let direction_hor = 5;
    let direction_vert = 0.5;
    let id = setInterval(frame, 1);

        function frame() {
            if (pos_hor == end) {
                direction_hor *= -1;
                direction_vert *= -1;
            }

            pos_hor += direction_hor;
            pos_vert += direction_vert;

            if (check == "c") {
                elem.style.bottom = pos_vert + "px";
                elem.style.left = pos_hor + "px";
            } else {
                elem.style.top = pos_vert + "px";
                elem.style.right = pos_hor + "px";
            }

            if (pos_hor == 0) {
                stop(id);
            }
        }
    }

function dice() {
    return Math.floor(Math.random() * 7);
}

function pause_submit(myform) {
    setTimeout(function() {
        myform.submit();
    }, 2000);
}

function heal(dom) {
    dom.style.backgroundColor = 'green';
    dom.style.color = 'green';
    setTimeout(function() {
        dom.style.backgroundColor = 'black';
        dom.style.color = 'black';
    }, 1000)
}

function slash(dom) {
    dom.style.backgroundColor = 'grey';
    dom.style.color = 'grey';
    setTimeout(function() {
        dom.style.backgroundColor = 'black';
        dom.style.color = 'black';
    }, 1000)
}
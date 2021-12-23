
/**************************************
    Preload people name list
 **************************************/
let people = [];

function search_person_from_people(peopleId) {
    var person = null;
    for(var i=0;i<people.length;i++){
        var p = people[i];
        if (p.peopleId === peopleId){
            person = p;
            break;
        }
    }
    return person;
}

function handle_loaded_people(people){
    autocomplete(document.getElementById("person"), people);
    for(var i=0;i<datas.length;i++){
        let person = datas[i];
        drawNameBox(person, true, true);
    }
}

/**************************************
    Draw Rectangle and Name Label
 **************************************/
let curr_pos = {};

function inBox(x, y) {
    for(var i=0;i<datas.length;i++){
        let position = datas[i];
        if(x >= position.pos_left && x <= position.pos_right && y >= position.pos_top && y <= position.pos_bottom) {
            position.idx = i;
            return position;
        }
    }
    return null;
}

function drawNameBox(person, drawRectangle, drawName) {
    if(drawRectangle === true){
        let element = document.createElement('div');
        element.id = 'face_' + person.pos_left + "_" + person.pos_top;
        element.className = 'rectangle';
        element.style.left = person.pos_left + 'px';
        element.style.top = person.pos_top + 'px';
        element.style.width = (person.pos_right - person.pos_left) + 'px';
        element.style.height = (person.pos_bottom - person.pos_top) + 'px';
        canvas.appendChild(element);
        canvas.style.cursor = "crosshair";
    }
    if(drawName === true){
        let min_width = 50;

        let width = person.pos_right - person.pos_left;
        let left = person.pos_left;
        if (width < min_width) {
            left = (left - (min_width - width) / 2);
            width = min_width;
        }

        var label = document.createElement('div');
        label.id = 'name_' + person.pos_left + "_" + person.pos_top;
        label.className = 'faceName';
        label.style.left = left + 'px';
        label.style.top = (person.pos_bottom + 2) + 'px';
        label.style.width = width + 'px';
        label.style.height = '16px';
        canvas.appendChild(label);
        label.innerHTML = person.peopleName;
    }
}

function initDraw(canvas) {
    function setMousePosition(e) {
        var ev = e || window.event; //Moz || IE
        if (ev.pageX) { //Moz
            mouse.x = ev.pageX + window.pageXOffset;
            mouse.y = ev.pageY + window.pageYOffset;
        } else if (ev.clientX) { //IE
            mouse.x = ev.clientX + document.body.scrollLeft;
            mouse.y = ev.clientY + document.body.scrollTop;
        }
    }

    var mouse = {
        x: 0,
        y: 0,
        startX: 0,
        startY: 0
    };
    var element = null;

    canvas.addEventListener('mousemove', function (e) {
        setMousePosition(e);
        if (element !== null) {
            element.style.width = Math.abs(mouse.x - mouse.startX) + 'px';
            element.style.height = Math.abs(mouse.y - mouse.startY) + 'px';
            element.style.left = (mouse.x - mouse.startX < 0) ? mouse.x + 'px' : mouse.startX + 'px';
            element.style.top = (mouse.y - mouse.startY < 0) ? mouse.y + 'px' : mouse.startY + 'px';
        }
    });

    canvas.onclick = function (e) {
        let exist_box = inBox(mouse.x, mouse.y);
        if (exist_box !== null){
            curr_pos = exist_box;
            openDialog(exist_box);
        }else {

            if (element !== null) {
                element = null;
                canvas.style.cursor = "default";
                console.log("draw rectangle finished.");

                let x = mouse.x;
                let y = mouse.y;

                curr_pos.pos_right = x;
                curr_pos.pos_bottom = y;
                curr_pos.peopleIdRecognized = '';
                curr_pos.peopleIdAssign = '';
                curr_pos.peopleId = '';
                curr_pos.peopleName = '';
                curr_pos.source = 'draw';

                datas.push(curr_pos);
                openDialog(curr_pos);

                drawNameBox(curr_pos, false, true);

            } else {
                console.log("draw rectangle begun.");
                let x = mouse.x;
                let y = mouse.y;
                mouse.startX = x;
                mouse.startY = y;
                element = document.createElement('div');
                element.id = 'face_' + x + "_" + y;
                element.className = 'rectangle';
                element.style.left = x + 'px';
                element.style.top = y + 'px';
                canvas.appendChild(element);
                canvas.style.cursor = "crosshair";

                curr_pos = {};
                curr_pos.div = element.id;
                curr_pos.pos_left = x;
                curr_pos.pos_top = y;
            }
        }
    }
}

/*********************
    Dialog
 *********************/

function closeDialog() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
}

function openDialog(item) {
    // Get the modal
    var modal = document.getElementById("myModal");
    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];
    // When the user clicks on <span> (x), close the modal
    span.onclick = function () {
        modal.style.display = "none";
    }
    modal.style.display = "block";
    clean_person_in_dialog();

    let canvas = document.getElementById('preview_canvas');
    let ctx = canvas.getContext('2d');
    let image = document.getElementById("img");
    let item_width = item.pos_right - item.pos_left;
    let item_height = item.pos_bottom - item.pos_top;
    let origin_scale = 80;
    let scale = origin_scale;
    if (Math.max(item_width, item_height) > origin_scale) {
        scale = origin_scale / Math.max(item_width, item_height) * origin_scale;
    }
    ctx.drawImage(image,
        item.pos_left, item.pos_top,   // Start at 70/20 pixels from the left and the top of the image (crop),
        item_width, item_height,   // "Get" a `50 * 50` (w * h) area from the source image (crop),
        0, 0,     // Place the result at 0, 0 in the canvas,
        scale, scale); // With as width / height: 100 * 100 (scale)

    if(item.peopleId !== ""){
        show_person_in_dialog(item.peopleId);
    }

}

/**************************************
    Dialog Text Fields
 **************************************/

function clean_person_in_dialog(){
    document.getElementById("person").value = "";
    document.getElementById("personName").value = "";
    document.getElementById("shortName").value = "";
    document.getElementById("message").innerHTML = "";
    document.getElementById("personName").removeAttribute("readOnly");
    document.getElementById("shortName").removeAttribute("readOnly");
    document.getElementById("personIconImg").src = unknown_person_icon;
}

function show_person_in_dialog(peopleId){
    if(peopleId !== "" && peopleId !== "Unknown") {
        let person = search_person_from_people(peopleId);
        if (person != null){
            document.getElementById("person").value = person.peopleId;
            document.getElementById("personName").value = person.name;
            document.getElementById("shortName").value = person.shortName;
            document.getElementById("personName").readOnly = true;
            document.getElementById("shortName").readOnly = true;
            if(person.icon_file_path !== ""){
                document.getElementById("personIconImg").src = "/view?file=" + person.icon_file_path;
            }else{
                document.getElementById("personIconImg").src = unknown_person_icon;
            }
        }else{
            document.getElementById("message").innerHTML = "No record matches.";
        }
    }
}

/**************************************
    Dialog Text Field Autocomplete
 **************************************/

function autocomplete(inp, arr) {
    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function (e) {
        var a, b, i, val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) {
            return false;
        }
        clean_person_in_dialog();
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/
        for (i = 0; i < arr.length; i++) {
            let candidate1 = arr[i].peopleId;
            let candidate2 = arr[i].name;
            let candidate3 = arr[i].shortName;
            /*check if the item starts with the same letters as the text field value:*/
            if (candidate1.substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                /*create a DIV element for each matching element:*/
                b = document.createElement("DIV");
                /*make the matching letters bold:*/
                b.innerHTML = "<strong>" + candidate1.substr(0, val.length) + "</strong>";
                b.innerHTML += candidate1.substr(val.length);
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML += "<input type='hidden' value='" + candidate1 + "'>";
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function (e) {
                    /*insert the value for the autocomplete text field:*/
                    inp.value = this.getElementsByTagName("input")[0].value;
                    /*close the list of autocompleted values,
                    (or any other open lists of autocompleted values:*/
                    closeAllLists();
                    show_person_in_dialog(inp.value);
                });
                a.appendChild(b);
            }else if (candidate2.substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                /*create a DIV element for each matching element:*/
                b = document.createElement("DIV");
                /*make the matching letters bold:*/
                b.innerHTML = "<strong>" + candidate2.substr(0, val.length) + "</strong>";
                b.innerHTML += candidate2.substr(val.length);
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML += "<input type='hidden' value='" + candidate1 + "'>";
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function (e) {
                    /*insert the value for the autocomplete text field:*/
                    inp.value = this.getElementsByTagName("input")[0].value;
                    /*close the list of autocompleted values,
                    (or any other open lists of autocompleted values:*/
                    closeAllLists();
                    show_person_in_dialog(inp.value);
                });
                a.appendChild(b);
            }else if (candidate3.substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                /*create a DIV element for each matching element:*/
                b = document.createElement("DIV");
                /*make the matching letters bold:*/
                b.innerHTML = "<strong>" + candidate2.substr(0, val.length) + "</strong>";
                b.innerHTML += candidate3.substr(val.length);
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML += "<input type='hidden' value='" + candidate1 + "'>";
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function (e) {
                    /*insert the value for the autocomplete text field:*/
                    inp.value = this.getElementsByTagName("input")[0].value;
                    /*close the list of autocompleted values,
                    (or any other open lists of autocompleted values:*/
                    closeAllLists();
                    show_person_in_dialog(inp.value);
                });
                a.appendChild(b);
            }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function (e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });

    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }

    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}

/**************************************
    Dialog Buttons
 **************************************/

function tag_it(){
    console.log("tag it")
    let peopleId = document.getElementById("person").value.trim();
    let peopleName = document.getElementById("personName").value.trim();
    let shortName = document.getElementById("shortName").value.trim();
    curr_pos.peopleIdAssign = peopleId
    curr_pos.peopleId = curr_pos.peopleIdAssign;

    for(var i=0;i<datas.length;i++){
        let p = datas[i];
        if(p.pos_left === curr_pos.pos_left && p.pos_right === curr_pos.pos_right && p.pos_top === curr_pos.pos_top && p.pos_bottom === curr_pos.pos_bottom) {
            p.peopleIdAssign = peopleId;
            p.peopleId = p.peopleIdAssign;
            p.peopleName = peopleName;
            let id = "name_" + curr_pos.pos_left + "_" + curr_pos.pos_top;
            document.getElementById(id).innerHTML = peopleName;
            break;
        }
    }
    closeDialog();
}

function untag_it(){
    console.log("untag it: "+ curr_pos.pos_left + ", " + curr_pos.pos_top)
    let canvas = document.getElementById('canvas');

    for(var i=0;i<datas.length;i++){
        let p = datas[i];
        if(p.pos_left === curr_pos.pos_left && p.pos_right === curr_pos.pos_right && p.pos_top === curr_pos.pos_top && p.pos_bottom === curr_pos.pos_bottom) {
            let rectangle = document.getElementById("face_" + curr_pos.pos_left + "_" + curr_pos.pos_top);
            let name = document.getElementById("name_" + curr_pos.pos_left + "_" + curr_pos.pos_top);
            canvas.removeChild(rectangle);
            canvas.removeChild(name);
            datas.splice(i, 1);
            break;
        }
    }
    closeDialog();
}

/**************************************
    SideNav Buttons
 **************************************/

function untag_all(){
    let canvas = document.getElementById('canvas');
    for(var i=0;i<datas.length;i++) {
        let data = datas[i];
        let rectangle_id = "face_" + data.pos_left + "_" + data.pos_top;
        let name_id = "name_" + data.pos_left + "_" + data.pos_top;
        let rectangle = document.getElementById(rectangle_id);
        let name = document.getElementById(name_id);
        canvas.removeChild(rectangle);
        canvas.removeChild(name);
    }
    datas = [];
}

function hide_tags() {
    for(var i=0;i<datas.length;i++) {
        let data = datas[i];
        let rectangle_id = "face_" + data.pos_left + "_" + data.pos_top;
        let name_id = "name_" + data.pos_left + "_" + data.pos_top;
        let rectangle = document.getElementById(rectangle_id);
        let name = document.getElementById(name_id);
        rectangle.style.display = "none";
        name.style.display = "none";
    }
}

function show_tags() {
    for(var i=0;i<datas.length;i++) {
        let data = datas[i];
        let rectangle_id = "face_" + data.pos_left + "_" + data.pos_top;
        let name_id = "name_" + data.pos_left + "_" + data.pos_top;
        let rectangle = document.getElementById(rectangle_id);
        let name = document.getElementById(name_id);
        rectangle.style.display = "block";
        name.style.display = "block";
    }
}

function restore_tags() {
    untag_all();
    datas = []
    for(var i=0;i<datas_backup.length;i++){
        datas.push(datas_backup[i]);
    }
    for(var i=0;i<datas.length;i++) {
        let data = datas[i];
        drawNameBox(data, true, true);
    }
}

/**************************************
    Web API calls
 **************************************/

let fetchQueryResult = (action, id) => {
    const xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4) {
            if (xmlHttp.status === 200) {
                //console.log(xmlHttp.responseText);
                let data = JSON.parse(xmlHttp.responseText);
                if (! Array.isArray(data)) {
                    data = JSON.parse("[" + xmlHttp.responseText +"]")
                }
                if (action === "people"){
                    people = data;
                    handle_loaded_people(people);

                }else{
                    console.log(data);
                }
            }else{
                const data = xmlHttp.responseText;
                console.log(data);
            }
        }
    };

    //document.getElementById("msg").innerText = "Executing ...";
    if (action === "people"){
        xmlHttp.open("GET", "/people", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }
}
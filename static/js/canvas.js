
let curr_pos = {};
let people = [];

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
        let obj = inBox(mouse.x, mouse.y);
        if(obj != null){
            console.log("it's "+ obj.idx + " - " + obj.peopleIdRecognized + " - " + obj.peopleId + " - " + obj.peopleName);
        }
    };

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
        if (element !== null) {
            element = null;
            canvas.style.cursor = "default";
            console.log("draw rectangle finished.");

            curr_pos.pos_right = mouse.x;
            curr_pos.pos_bottom = mouse.y;
            curr_pos.peopleIdRecognized = '';
            curr_pos.peopleIdAssign = 'Unknown';
            curr_pos.peopleId = 'Unknown';
            curr_pos.peopleName = '';
            curr_pos.source = 'draw';

            console.log(curr_pos);
            datas.push(curr_pos);
            openDialog(curr_pos);
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

    let canvas = document.getElementById('preview_canvas');
    let ctx = canvas.getContext('2d');
    let image = document.getElementById("img");
    let item_width = item.pos_right - item.pos_left + 5;
    let item_height = item.pos_bottom - item.pos_top + 5;
    let scale = 100;
    if (Math.max(item_width, item_height) > 75) {
        scale = 75 / Math.max(item_width, item_height) * 100;
    }
    ctx.drawImage(image,
        item.pos_left, item.pos_top,   // Start at 70/20 pixels from the left and the top of the image (crop),
        item_width, item_height,   // "Get" a `50 * 50` (w * h) area from the source image (crop),
        0, 0,     // Place the result at 0, 0 in the canvas,
        scale, scale); // With as width / height: 100 * 100 (scale)
}

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
                    autocomplete(document.getElementById("person"), people);
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
        clean_person();
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
                    show_person(inp.value);
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
                    show_person(inp.value);
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
                    show_person(inp.value);
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

function tag_it(){
    console.log("tag it")
}

function untag_it(){
    console.log("untag it")
}

function clean_person(){
    document.getElementById("message").innerHTML = "";
    document.getElementById("personName").value = "";
    document.getElementById("shortName").value = "";
    document.getElementById("message").innerHTML = "";
    document.getElementById("personName").removeAttribute("readOnly");
    document.getElementById("shortName").removeAttribute("readOnly");
    document.getElementById("personIconImg").src = unknown_person_icon;
}

function show_person(peopleId){
    var person = null;
    for(var i=0;i<people.length;i++){
        var p = people[i];
        if (p.peopleId === peopleId){
            person = p;
            break;
        }
    }
    if (person != null){
        document.getElementById("personName").value = person.name;
        document.getElementById("shortName").value = person.shortName;
        document.getElementById("personName").readOnly = true;
        document.getElementById("shortName").readOnly = true;
        document.getElementById("personIconImg").src = "/view?file=" + person.icon_file_path;
        console.log(person);
    }else{
        document.getElementById("message").innerHTML = "No record matches.";
    }
}
let streamQueryResult = (action, columns, progress_column, id) => {
    createChunkedTable(columns);
    const xmlHttp = new XMLHttpRequest();
    var last_response_index = 0;
    xmlHttp.onprogress = function () {
        let responseText = xmlHttp.responseText;
        let current_response_index = responseText.length;

        if (last_response_index !== current_response_index) {
            var just_received = responseText.substring(last_response_index, current_response_index);
            last_response_index = current_response_index;
            var just_received_lines = just_received.replaceAll("}{", "}\n{").split("\n");
            for (let i=0;i<just_received_lines.length;i++) {
                let line = just_received_lines[i];
                console.log(line);
                addRowToChunkedTable(columns, line, progress_column);
            }
        }
    };
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4) {
            if (xmlHttp.status < 300) {
                console.log("stream done");
                document.getElementById("msg").innerText = "Received data at "+ new Date().toLocaleString();
            }else{
                const data = xmlHttp.responseText;
                document.getElementById("msg").innerText = data;
            }
        }
    };

    document.getElementById("msg").innerText = "Executing ...";
    if(action === "start_training"){
        xmlHttp.open("GET", "/training/start", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "start_recognition"){
        xmlHttp.open("GET", "/recognition/start", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "sync_back_faces"){
        xmlHttp.open("GET", "/sync/faces", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }
}

let fetchQueryResult = (action, id) => {
    const xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState === 4) {
            if (xmlHttp.status === 200) {
                console.log(xmlHttp.responseText);
                let data = JSON.parse(xmlHttp.responseText);
                if (! Array.isArray(data)) {
                    data = JSON.parse("[" + xmlHttp.responseText +"]")
                }
                document.getElementById("msg").innerText = "Received data at "+ new Date().toLocaleString();
                tableFromJson(data);
            }else{
                const data = xmlHttp.responseText;
                document.getElementById("msg").innerText = data;
            }
        }
    };

    document.getElementById("msg").innerText = "Executing ...";
    if (action === "job_status"){
        xmlHttp.open("GET", "/job/list", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "stop_job"){
        xmlHttp.open("GET", "/job/stop", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "force_stop_job"){
        xmlHttp.open("GET", "/job/force/stop/" + id, true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "resume_job"){
        xmlHttp.open("GET", "/job/start", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "health"){
        xmlHttp.open("GET", "/health", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "copy_images"){
        xmlHttp.open("GET", "/images/copy", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "list_faces"){
        xmlHttp.open("GET", "/images/list", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "list_scanned_faces"){
        xmlHttp.open("GET", "/images/scanned/faces", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "use_dataset"){
        xmlHttp.open("GET", "/dataset/use/"+ id, true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "list_dataset_files"){
        xmlHttp.open("GET", "/dataset/list", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "list_dataset_people"){
        xmlHttp.open("GET", "/dataset/people", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "list_dataset_of_people"){
        xmlHttp.open("GET", "/dataset/list/people/" + id, true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "list_dataset_backups"){
        xmlHttp.open("GET", "/dataset/backups", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "list_model"){
        xmlHttp.open("GET", "/model/list", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "list_model_backups"){
        xmlHttp.open("GET", "/model/backups", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "backup_model"){
        xmlHttp.open("GET", "/model/backup", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "toggle_face_sample"){
        xmlHttp.open("GET", "/face/toggle/sample/" + id, true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "toggle_face_scan_result"){
        xmlHttp.open("GET", "/face/toggle/scan/result/" + id, true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "toggle_scanned_face_sample"){
        xmlHttp.open("GET", "/face/scanned/toggle/sample/" + id, true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }else if(action === "toggle_scanned_face_scan_result"){
        xmlHttp.open("GET", "/face/scanned/toggle/scan/result/" + id, true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
    }
}

let createChunkedTable = (columns) => {
    // Create a table.
    const table = document.createElement("table");
    table.id = "chunkedTable";

    // Create table header row.
    let tr = table.insertRow(-1);                   // table row.

    for (let i = 0; i < columns.length; i++) {
        let th = document.createElement("th");      // table header.
        th.innerHTML = columns[i];
        tr.appendChild(th);
    }

    const divShowData = document.getElementById('showData');
    divShowData.innerHTML = "";
    divShowData.appendChild(table);
}

let addRowToChunkedTable = (columns, message, progress_column) => {
    let table = document.getElementById("chunkedTable");
    let tr = table.insertRow(-1);

    if (message[0] === "{") {
        let json = JSON.parse(message);
        for (let j = 0; j < columns.length; j++) {
            let column = columns[j];
            let tabCell = tr.insertCell(-1);
            tabCell.innerText = json[column];
            if (column === progress_column) {
                document.getElementById("msg").innerText = "Executing " + json[column] + " ..."
            }
        }
    }else{
        for (let j = 0; j < columns.length; j++) {
            let tabCell = tr.insertCell(-1);
            tabCell.innerText = message;
        }
    }
}

let tableFromJson = (arrayData) => {

    // Extract value from table header.
    // ('Book ID', 'Book Name', 'Category' and 'Price')
    let col = [];
    for (let i = 0; i < arrayData.length; i++) {
        for (let key in arrayData[i]) {
            if (col.indexOf(key) === -1) {
                col.push(key);
            }
        }
    }

    // Create a table.
    const table = document.createElement("table");

    // Create table header row using the extracted headers above.
    let tr = table.insertRow(-1);                   // table row.

    for (let i = 0; i < col.length; i++) {
        let th = document.createElement("th");      // table header.
        th.innerHTML = col[i];
        tr.appendChild(th);
    }

    // add json data to the table as rows.
    for (let i = 0; i < arrayData.length; i++) {

        tr = table.insertRow(-1);

        for (let j = 0; j < col.length; j++) {
            let tabCell = tr.insertCell(-1);
            let header = col[j];
            let node = arrayData[i][col[j]];
            if (header === "actions") {
                if(Array.isArray(node)){
                    for (let k = 0; k < node.length; k++){
                        let action = node[k];
                        let button="<input type='button' onclick='"
                            + action["func"] +"(\""+ action["id"] +"\")' value='"+ action["func"] +"' />&nbsp;"
                        tabCell.innerHTML += button;
                    }
                }else{
                    tabCell.innerHTML = node;
                }
            } else {
                if(typeof node === 'object' && node !== null) {
                    let text = node["text"];
                    let actions = node["actions"];
                    if (text !== undefined && text !== null) {
                        tabCell.innerHTML += text + "&nbsp;";
                    }
                    if (actions !== undefined && actions !== null && Array.isArray(actions)){
                        for (let k = 0; k < actions.length; k++){
                            let action = actions[k];
                            if (action["func"] === "view") {
                                if (action["id"] !== "") {
                                    let link = "<a href='/view?file=" + action["id"] + "' target='_blank'>view</a>&nbsp;"
                                    tabCell.innerHTML += link;
                                }
                            }else if (action["func"] === "canvas") {
                                if (action["id"] !== "") {
                                    let link = "<a href='/canvas?file=" + action["id"] + "' target='_blank'>canvas</a>&nbsp;"
                                    tabCell.innerHTML += link;
                                }
                            }else if (action["func"] === "thumbnail") {
                                if (action["id"] !== "") {
                                    let link="<img src='/view?file=" + action["id"] +"'  alt='thumbnail'/>&nbsp;"
                                    tabCell.innerHTML += link;
                                }
                            }else{
                                let button="<input type='button' onclick='"
                                    + action["func"] +"(\""+ action["id"] +"\")' value='"+ action["func"] +"' />&nbsp;"
                                tabCell.innerHTML += button;
                            }
                        }
                    }
                }else{
                    tabCell.innerHTML = node;
                }
            }
        }
    }

    // Now, add the newly created table with json data, to a container.
    const divShowData = document.getElementById('showData');
    divShowData.innerHTML = "";
    divShowData.appendChild(table);
}
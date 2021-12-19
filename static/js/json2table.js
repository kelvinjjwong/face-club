let fetchQueryResult = (action) => {
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
    }else if(action === "list_dataset_backups"){
        xmlHttp.open("GET", "/dataset/backups", true);
        xmlHttp.setRequestHeader("Content-type", "text/plain");
        xmlHttp.send();
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
            let text = arrayData[i][col[j]];
            if (header === "actions") {
                if(Array.isArray(text)){
                    for (let k = 0; k < text.length; k++){
                        let action = text[k];
                        let button="<input type='button' onclick='"
                            + action["func"] +"(\""+ action["id"] +"\")' value='"+ action["func"] +"' />&nbsp;"
                        tabCell.innerHTML += button;
                    }
                }else{
                    tabCell.innerHTML = text;
                }
            } else {
                tabCell.innerHTML = text;
            }
        }
    }

    // Now, add the newly created table with json data, to a container.
    const divShowData = document.getElementById('showData');
    divShowData.innerHTML = "";
    divShowData.appendChild(table);
}
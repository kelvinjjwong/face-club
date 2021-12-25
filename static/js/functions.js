function stop_job(id) {
    fetchQueryResult("stop_job")
}

function force_stop_job(id) {
    fetchQueryResult("force_stop_job", id)
}

function resume_job(id){
    fetchQueryResult("resume_job")
}

function toggle_scan_result(id) {
    fetchQueryResult("toggle_face_scan_result", id)
}

function toggle_sample(id){
    fetchQueryResult("toggle_face_sample", id)
}

function scanned_toggle_scan_result(id) {
    fetchQueryResult("toggle_scanned_face_scan_result", id)
}

function scanned_toggle_sample(id){
    fetchQueryResult("toggle_scanned_face_sample", id)
}

function use_dataset(backup_folder){
    fetchQueryResult("use_dataset", backup_folder)
}

function dataset_of_people(peopleId){
    fetchQueryResult("list_dataset_of_people", peopleId)
}

function backup_model(){
    fetchQueryResult("backup_model")
}
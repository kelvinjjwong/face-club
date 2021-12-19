function stop_job(id) {
    fetchQueryResult("stop_job")
}

function kill_job(id) {
    // TODO kill job
    console.log("kill job: "+ id)
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

function use_dataset(backup_folder){
    // TODO use dataset
    console.log("use dataset backup folder: "+ backup_folder)
}
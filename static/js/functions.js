function stop_job(id) {
    fetchQueryResult("stop_job")
}

function force_stop_job(id) {
    fetchQueryResult("force_stop_job", id)
}

function resume_job(id){
    fetchQueryResult("resume_job")
}

function toggle_reviewed(id) {
    fetchQueryResult("toggle_reviewed", id)
}

function toggle_sample(id){
    fetchQueryResult("toggle_sample", id)
}

function toggle_reviewed_tagged(id) {
    fetchQueryResult("toggle_reviewed_tagged", id)
}

function toggle_sample_tagged(id){
    fetchQueryResult("toggle_sample_tagged", id)
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
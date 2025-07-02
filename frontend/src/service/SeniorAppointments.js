export const seniorAppointments = {
    getAppointmentData(){
        return [
            {doc_id:'1', name: "Dr. Sharma", date:"Wed 14 May", time:"5:00 PM"},
            {doc_id:'1', name: "Dr. Sharma", date:"Wed 21 May", time:"5:00 PM"},
            {doc_id:'1', name: "Dr. Sharma", date:"Thu 28 May", time:"5:00 PM"},
        ]
    },
    getAppointments() {
        return Promise.resolve(this.getAppointmentData());
    },
}

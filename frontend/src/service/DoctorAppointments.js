export const doctorAppointments = {
    getData(){
        return [
            {sen_id:'1', label: "Mr. Mishra's Appointment", date:"Wed 14 May", time:"5:00 PM"},
            {sen_id:'2', label: "Mr. Chopra's Appointment", date:"Wed 14 May", time:"5:30 PM"},
            {sen_id:'3', label: "Mr. Mehra's Appointment", date:"Thu 15 May", time:"5:00 PM"},
            {sen_id:'4', label: "Mrs. Shanti's Appointment", date:"Thu 15 May", time:"5:30 PM"},
            {sen_id:'5', label: "Mr. Anupam's Appointment", date:"Fri 16 May", time:"5:00 PM"},
        ]
    },
    getAppointments() {
        return Promise.resolve(this.getData());
    },
}

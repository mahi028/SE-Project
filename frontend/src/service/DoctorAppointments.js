export const doctorAppointments = {
    getAppointmentData(){
        return [
            {sen_id:'1', name: "Mr. Mishra", date:"Wed 14 May", time:"5:00 PM"},
            {sen_id:'2', name: "Mr. Chopra", date:"Wed 14 May", time:"5:30 PM"},
            {sen_id:'3', name: "Mr. Mehra", date:"Thu 15 May", time:"5:00 PM"},
            {sen_id:'4', name: "Mrs. Shanti", date:"Thu 15 May", time:"5:30 PM"},
            {sen_id:'5', name: "Mr. Anupam", date:"Fri 16 May", time:"5:00 PM"},
        ]
    },
    getAppointmentRequestData(){
        return [
            {sen_id:'1', name: "Mr. Sharma", date:"Wed 16 May", time:"5:30 PM", reason:"I am facing frequent pain in my knee joint.", profile:"https://www.wockhardthospitals.com/wp-content/uploads/2023/05/shutterstock_365746949-scaled_11zon.webp"},
            {sen_id:'2', name: "Mr. Gupta", date:"Wed 17 May", time:"5:00 PM", reason:"My Legs ache whenever I take a brief walk.", profile:"https://www.shutterstock.com/image-photo/portrait-smiling-senior-man-using-260nw-573623944.jpg"},
            {sen_id:'3', name: "Mrs. Sheetal", date:"Thu 17 May", time:"5:30 PM", reason:"My back hurts everytime I do something,", profile:"https://manipaltrutest.s3.ap-south-1.amazonaws.com/package-images/package-images-1675573993564-280013-senior-citizen-women.jpg"},
        ]
    },
    getAppointments() {
        return Promise.resolve(this.getAppointmentData());
    },
    getAppointmentRequests() {
        return Promise.resolve(this.getAppointmentRequestData());
    },
}

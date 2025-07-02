export const seniorSchedules = {
    getScheuldeData(){
        return [
            {schedule_id:'1', label: "XYZ Tablet", date:"EveryDay", time:["9:00 AM"]},
            {schedule_id:'2', label: "ABC Syrup", date:"EveryDay", time:["9:00 PM"]},
            {schedule_id:'3', label: "PQR Tablet", date:"Everyday", time:["9:00 PM"]},
        ]
    },
    getScheuldes() {
        return Promise.resolve(this.getScheuldeData());
    },
};
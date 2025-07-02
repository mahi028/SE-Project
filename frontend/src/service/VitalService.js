export const vitals = {
    getVitalData(){
        return [
            { label: "XYZ", date: "10 Aug", time: "9:00", value: "100" },
            { label: "ABC", date: "11 Aug", time: "10:00", value: "100" },
        ];
    },
    getVitals() {
        return Promise.resolve(this.getVitalData());
    },
};
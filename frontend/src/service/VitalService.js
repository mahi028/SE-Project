export const vitals = {
    getVitalTypes() {
        return [
            {
                label: "Blood Pressure",
                value: "blood_pressure",
                unit: "mmHg",
                placeholder: "120/80",
                thresholds: {
                    systolic: { low: 90, high: 140 },
                    diastolic: { low: 60, high: 90 }
                }
            },
            {
                label: "Blood Sugar",
                value: "blood_sugar",
                unit: "mg/dL",
                placeholder: "100",
                thresholds: { low: 70, high: 140 }
            },
            {
                label: "Heart Rate",
                value: "heart_rate",
                unit: "bpm",
                placeholder: "72",
                thresholds: { low: 60, high: 100 }
            },
            {
                label: "Body Temperature",
                value: "body_temperature",
                unit: "°F",
                placeholder: "98.6",
                thresholds: { low: 97.0, high: 99.5 }
            },
            {
                label: "Weight",
                value: "weight",
                unit: "kg",
                placeholder: "70",
                thresholds: null // Weight thresholds vary by individual
            },
            {
                label: "Oxygen Saturation",
                value: "oxygen_saturation",
                unit: "%",
                placeholder: "98",
                thresholds: { low: 95, high: null } // Only low threshold matters
            }
        ];
    },

    evaluateVitalStatus(vitalType, reading) {
        const type = this.getVitalTypes().find(t => t.value === vitalType);
        if (!type || !type.thresholds) {
            return { status: 'irrelevant', color: 'text-gray-500' };
        }

        const thresholds = type.thresholds;

        // Special handling for blood pressure
        if (vitalType === 'blood_pressure') {
            const match = reading.match(/(\d+)\/(\d+)/);
            if (!match) return { status: 'invalid', color: 'text-gray-500' };

            const systolic = parseInt(match[1]);
            const diastolic = parseInt(match[2]);

            if (systolic < thresholds.systolic.low || diastolic < thresholds.diastolic.low) {
                return { status: 'Low', color: 'text-red-600' };
            }
            if (systolic > thresholds.systolic.high || diastolic > thresholds.diastolic.high) {
                return { status: 'High', color: 'text-red-600' };
            }
            return { status: 'Safe', color: 'text-green-600' };
        }

        // For other vitals
        const value = parseFloat(reading);
        if (isNaN(value)) return { status: 'invalid', color: 'text-gray-500' };

        if (thresholds.low && value < thresholds.low) {
            return { status: 'Low', color: 'text-red-600' };
        }
        if (thresholds.high && value > thresholds.high) {
            return { status: 'High', color: 'text-red-600' };
        }
        return { status: 'Safe', color: 'text-green-600' };
    },

    getVitalData(){
        return [
            // S001 vitals - multiple readings for trend visualization
            {
                id: 1,
                sen_id: "S001",
                label: "Blood Pressure",
                value: "blood_pressure",
                unit: "mmHg",
                date: "2024-05-10",
                time: "09:00 AM",
                reading: "120/80",
                loggedAt: "2024-05-10T09:00:00"
            },
            {
                id: 2,
                sen_id: "S001",
                label: "Blood Pressure",
                value: "blood_pressure",
                unit: "mmHg",
                date: "2024-05-12",
                time: "09:15 AM",
                reading: "125/82",
                loggedAt: "2024-05-12T09:15:00"
            },
            {
                id: 3,
                sen_id: "S001",
                label: "Blood Pressure",
                value: "blood_pressure",
                unit: "mmHg",
                date: "2024-05-14",
                time: "09:30 AM",
                reading: "118/78",
                loggedAt: "2024-05-14T09:30:00"
            },
            {
                id: 4,
                sen_id: "S001",
                label: "Blood Sugar",
                value: "blood_sugar",
                unit: "mg/dL",
                date: "2024-05-11",
                time: "10:00 AM",
                reading: "110",
                loggedAt: "2024-05-11T10:00:00"
            },
            {
                id: 5,
                sen_id: "S001",
                label: "Blood Sugar",
                value: "blood_sugar",
                unit: "mg/dL",
                date: "2024-05-13",
                time: "10:15 AM",
                reading: "105",
                loggedAt: "2024-05-13T10:15:00"
            },
            {
                id: 6,
                sen_id: "S001",
                label: "Blood Sugar",
                value: "blood_sugar",
                unit: "mg/dL",
                date: "2024-05-15",
                time: "10:30 AM",
                reading: "115",
                loggedAt: "2024-05-15T10:30:00"
            },
            {
                id: 7,
                sen_id: "S001",
                label: "Heart Rate",
                value: "heart_rate",
                unit: "bpm",
                date: "2024-05-10",
                time: "08:00 AM",
                reading: "72",
                loggedAt: "2024-05-10T08:00:00"
            },
            {
                id: 8,
                sen_id: "S001",
                label: "Heart Rate",
                value: "heart_rate",
                unit: "bpm",
                date: "2024-05-12",
                time: "08:15 AM",
                reading: "75",
                loggedAt: "2024-05-12T08:15:00"
            },
            {
                id: 9,
                sen_id: "S001",
                label: "Heart Rate",
                value: "heart_rate",
                unit: "bpm",
                date: "2024-05-14",
                time: "08:30 AM",
                reading: "70",
                loggedAt: "2024-05-14T08:30:00"
            },
            {
                id: 10,
                sen_id: "S002",
                label: "Heart Rate",
                value: "heart_rate",
                unit: "bpm",
                date: "2024-05-12",
                time: "08:30 AM",
                reading: "75",
                loggedAt: "2024-05-12T08:30:00"
            },
            {
                id: 11,
                sen_id: "S002",
                label: "Body Temperature",
                value: "body_temperature",
                unit: "°F",
                date: "2024-05-13",
                time: "07:15 AM",
                reading: "98.6",
                loggedAt: "2024-05-13T07:15:00"
            },
            {
                id: 12,
                sen_id: "S002",
                label: "Body Temperature",
                value: "body_temperature",
                unit: "°F",
                date: "2024-05-15",
                time: "07:30 AM",
                reading: "98.4",
                loggedAt: "2024-05-15T07:30:00"
            },
            {
                id: 13,
                sen_id: "S003",
                label: "Weight",
                value: "weight",
                unit: "kg",
                date: "2024-05-14",
                time: "06:30 AM",
                reading: "72",
                loggedAt: "2024-05-14T06:30:00"
            },
            {
                id: 14,
                sen_id: "S003",
                label: "Weight",
                value: "weight",
                unit: "kg",
                date: "2024-05-16",
                time: "06:45 AM",
                reading: "71.5",
                loggedAt: "2024-05-16T06:45:00"
            }
        ];
    },

    getVitalsBySenior(seniorEzId) {
        const vitals = this.getVitalData().filter(vital => vital.sen_id === seniorEzId)
            .map(vital => ({
                ...vital,
                statusInfo: this.evaluateVitalStatus(vital.value, vital.reading)
            }));
        return Promise.resolve(vitals);
    },

    getVitals() {
        return Promise.resolve(this.getVitalData());
    },

    addVital(vitalData) {
        const vitals = this.getVitalData();
        const now = new Date();
        const newVital = {
            id: vitals.length + 1,
            ...vitalData,
            date: now.toISOString().split('T')[0],
            time: now.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            }),
            loggedAt: now.toISOString()
        };

        // Add status evaluation
        newVital.statusInfo = this.evaluateVitalStatus(newVital.value, newVital.reading);

        vitals.push(newVital);
        return Promise.resolve(newVital);
    }
};

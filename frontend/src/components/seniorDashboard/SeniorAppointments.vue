<script setup>
import { seniorAppointments } from '@/service/SeniorAppointments';
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const appointments = ref([]);
const visible = ref(false);

const newAppointment = ref({
    name: '',
    date: '',
    time: ''
});

const fetchAppointments = () => {
    seniorAppointments.getAppointments().then((data) => (appointments.value = data));
};

const showAddDialog = () => {
    visible.value = true;
};

const addAppointment = () => {
    if (newAppointment.value.name && newAppointment.value.date && newAppointment.value.time) {
        appointments.value.push({ ...newAppointment.value });
        toast.add({ severity: 'success', summary: 'Added', detail: 'Appointment Added', life: 3000 });
        visible.value = false;
        newAppointment.value = { name: '', date: '', time: '' };
    } else {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Fill all fields', life: 3000 });
    }
};

onMounted(() => {
    fetchAppointments();
});
</script>

<template>
    <Toast />
    <div class="card">
        <div class="flex items-center justify-between mb-4">
            <span class="text-xl font-bold">Appointments</span>
            <Button label="Add Appointment" icon="pi pi-plus" @click="showAddDialog" />
        </div>
        <DataTable :value="appointments" :rows="5" :paginator="true" responsiveLayout="scroll">
            <Column field="name" header="Name" style="width: 30%"></Column>
            <Column field="date" header="Date" style="width: 30%"></Column>
            <Column field="time" header="Time" style="width: 30%"></Column>
            <Column header="View" style="width: 10%">
                <template #body>
                    <RouterLink to="#"><Button icon="pi pi-search" type="button" class="p-button-text" /></RouterLink>
                </template>
            </Column>
        </DataTable>

        <Dialog v-model:visible="visible" modal header="Add Appointment" :style="{ width: '30rem' }">
            <div class="flex flex-col gap-4">
                <label for="name" class="text-sm font-medium text-gray-700">Doctor Name</label>
                <InputText id="name" v-model="newAppointment.name" class="w-full" />

                <label for="date" class="text-sm font-medium text-gray-700">Date</label>
                <InputText id="date" v-model="newAppointment.date" class="w-full" />

                <label for="time" class="text-sm font-medium text-gray-700">Time</label>
                <InputText id="time" v-model="newAppointment.time" class="w-full" />

                <Button label="Save Appointment" class="w-full mt-2" @click="addAppointment" />
            </div>
        </Dialog>
    </div>
</template>
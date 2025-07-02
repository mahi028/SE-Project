<script setup>
import { seniorSchedules } from '@/service/SeniorScheduleSevice';
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const schedules = ref([]);
const visible = ref(false);

const newSchedule = ref({
    label: '',
    date: '',
    time: ''
});

const fetchSchedules = () => {
    seniorSchedules.getScheuldes().then((data) => (schedules.value = data));
};

const showAddDialog = () => {
    visible.value = true;
};

const addSchedule = () => {
    if (newSchedule.value.label && newSchedule.value.date && newSchedule.value.time) {
        schedules.value.push({
            ...newSchedule.value,
            time: newSchedule.value.time.split(',').map((t) => t.trim())
        });
        toast.add({ severity: 'success', summary: 'Added', detail: 'Schedule Added', life: 3000 });
        visible.value = false;
        newSchedule.value = { label: '', date: '', time: '' };
    } else {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Fill all fields', life: 3000 });
    }
};

onMounted(() => {
    fetchSchedules();
});
</script>

<template>
    <Toast />
    <div class="card">
        <div class="flex items-center justify-between mb-4">
            <span class="text-xl font-bold">Medicinal Schedules</span>
            <Button label="Add Schedule" icon="pi pi-plus" @click="showAddDialog" />
        </div>
        <DataTable :value="schedules" :rows="5" :paginator="true" responsiveLayout="scroll">
            <Column field="label" header="Label" style="width: 30%"></Column>
            <Column field="date" header="Date" style="width: 30%"></Column>
            <Column field="time" header="Time" style="width: 30%">
                <template #body="slotProps">
                    {{ slotProps.data.time.join(', ') }}
                </template>
            </Column>
            <Column header="View" style="width: 10%">
                <template #body>
                    <RouterLink to="#"><Button icon="pi pi-search" type="button" class="p-button-text" /></RouterLink>
                </template>
            </Column>
        </DataTable>

        <Dialog v-model:visible="visible" modal header="Add Medicine Schedule" :style="{ width: '30rem' }">
            <div class="flex flex-col gap-4">
                <label for="label" class="text-sm font-medium text-gray-700">Medicine Label</label>
                <InputText id="label" v-model="newSchedule.label" class="w-full" />

                <label for="date" class="text-sm font-medium text-gray-700">Date (e.g. Everyday)</label>
                <InputText id="date" v-model="newSchedule.date" class="w-full" />

                <label for="time" class="text-sm font-medium text-gray-700">Time(s) (comma-separated)</label>
                <InputText id="time" v-model="newSchedule.time" class="w-full" />

                <Button label="Save Schedule" class="w-full mt-2" @click="addSchedule" />
            </div>
        </Dialog>
    </div>
</template>

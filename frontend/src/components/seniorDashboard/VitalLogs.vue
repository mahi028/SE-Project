<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { vitals as vitalService } from '@/service/VitalService';

const toast = useToast();

const vitals = ref([]);
const visible = ref(false);

const vitalForm = ref({
    label: '',
    date: '',
    time: '',
    value: ''
});

onMounted(() => {
    vitalService.getVitals().then((data) => {
        vitals.value = data;
    });
});

const openVitalDialog = () => {
    visible.value = true;
};

const submitVital = () => {
    if (vitalForm.value.label && vitalForm.value.date && vitalForm.value.time && vitalForm.value.value) {
        vitals.value.push({ ...vitalForm.value });
        toast.add({ severity: 'success', summary: 'Logged', detail: 'Vital Logged Successfully', life: 3000 });
        visible.value = false;
        vitalForm.value = { label: '', date: '', time: '', value: '' };
    } else {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Please fill all fields', life: 3000 });
    }
};
</script>

<template>
    <Toast />
    <div class="card">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
            <span class="text-xl font-bold">Vital Logs</span>
            <Button label="Log Vital" icon="pi pi-plus" @click="openVitalDialog" class="bg-green-100 text-green-600" />
        </div>

        <DataTable :value="vitals" :rows="5" :paginator="true" responsiveLayout="scroll">
            <Column field="label" header="Label" />
            <Column field="date" header="Date" />
            <Column field="time" header="Time" />
            <Column field="value" header="Value" />
            <Column header="View">
                <template #body>
                    <Button icon="pi pi-search" class="p-button-text" />
                </template>
            </Column>
        </DataTable>

        <!-- Vital Log Overlay Dialog -->
        <Dialog v-model:visible="visible" modal header="Log Vital" :style="{ width: '30rem' }">
            <div class="flex flex-col gap-4">
                <label for="label" class="text-sm font-medium text-gray-700">Label</label>
                <InputText id="label" v-model="vitalForm.label" class="w-full" />

                <label for="date" class="text-sm font-medium text-gray-700">Date</label>
                <InputText id="date" v-model="vitalForm.date" class="w-full" placeholder="e.g. Sunday, Everyday" />

                <label for="time" class="text-sm font-medium text-gray-700">Time</label>
                <InputText id="time" v-model="vitalForm.time" class="w-full" placeholder="e.g. 5:00 PM" />

                <label for="value" class="text-sm font-medium text-gray-700">Value</label>
                <InputText id="value" v-model="vitalForm.value" class="w-full" placeholder="e.g. 120/80, 98°F etc." />

                <div class="flex justify-end mt-2">
                    <Button label="Submit" icon="pi pi-check" class="bg-green-500 text-white" @click="submitVital" />
                </div>
            </div>
        </Dialog>
    </div>
</template>

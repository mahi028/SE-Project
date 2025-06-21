<script setup>
import { doctorAppointments } from '@/service/DoctorAppointments';
import { onMounted, ref } from 'vue';

const appointments = ref(null);

onMounted(() => {
    doctorAppointments.getAppointments().then((data) => (appointments.value = data));
});
</script>

<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">Appointments</div>
        <DataTable :value="appointments" :rows="5" :paginator="true" responsiveLayout="scroll">
            <Column field="label" header="Label" style="width: 30%"></Column>
            <Column field="date" header="Date" :sortable="true" style="width: 30%"></Column>
            <Column field="time" header="TIme" style="width: 30%"></Column>
            <Column style="width: 15%" header="View">
                <template #body>
                    <RouterLink to="#"> <!-- :to="/sen/{{ ezId }}" -->
                        <Button icon="pi pi-search" type="button" class="p-button-text"></Button>
                    </RouterLink>
                </template>
            </Column>
        </DataTable>
    </div>
</template>

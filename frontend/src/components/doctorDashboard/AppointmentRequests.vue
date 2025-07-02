<script setup>
import { doctorAppointments } from '@/service/DoctorAppointments';
import { onMounted, ref } from 'vue';
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";

const toast = useToast();
const confirm = useConfirm();
const appointments = ref(null);

onMounted(() => {
    doctorAppointments.getAppointmentRequests().then((data) => (appointments.value = data));
});

const visible = ref(false);
const selectedAppointment = ref(null);

const displayAppointment = (appointment) => {
    visible.value = false;
    selectedAppointment.value = appointment;
    visible.value = true;
}

const confimrAcceptRequest = (event) => {
    confirm.require({
        target: event.currentTarget,
        message: 'Are you sure you want to Accept?',
        icon: 'pi pi-exclamation-triangle',
        rejectProps: {
            label: 'Cancel',
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: 'Save'
        },
        accept: () => {
            appointments.value = appointments.value.filter((appointemnt)=> {return appointemnt.sen_id != selectedAppointment.value.sen_id})
            selectedAppointment.value = false;
            visible.value = false;
            toast.add({ severity: 'info', summary: 'Confirmed', detail: 'You have accepted', life: 3000 });
        },
    });
};
const confirmRejectRequest = (event) => {
    confirm.require({
        target: event.currentTarget,
        message: 'Do you want to reject this Request?',
        icon: 'pi pi-info-circle',
        rejectProps: {
            label: 'Cancel',
            severity: 'secondary',
            outlined: true
        },
        acceptProps: {
            label: 'Delete',
            severity: 'danger'
        },
        accept: () => {
            appointments.value = appointments.value.filter((appointemnt)=> {return appointemnt.sen_id != selectedAppointment.value.sen_id})
            selectedAppointment.value = false;
            visible.value = false;
            toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Record deleted', life: 3000 });
        },
    });
};

</script>

<template>
    <Toast />
    <ConfirmPopup></ConfirmPopup>
    <div class="card">
        <div class="font-semibold text-xl mb-4">Appointment Requests</div>
        <DataTable :value="appointments" :rows="5" :paginator="true" responsiveLayout="scroll">
            <Column field="name" header="Name" style="width: 30%"></Column>
            <Column field="date" header="Date" :sortable="true" style="width: 30%"></Column>
            <Column field="time" header="Time" style="width: 30%"></Column>
            <Column header="Details" class="w-1/6">
                <template #body="slotProps">
                    <Button type="button" @click="displayAppointment(slotProps.data)" icon="pi pi-search" severity="secondary" rounded></Button>
                </template>
            </Column>
        </DataTable>
        <Dialog v-model:visible="visible" modal header="Appointment Details" :style="{ width: '45rem' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
            <div v-if="selectedAppointment" class="flex flex-col gap-4">
                <!-- Profile Image and Basic Info -->
                <div class="flex gap-4 items-start">
                    <div class="flex-shrink-0">
                        <img
                            :src="selectedAppointment.profile || '/default-avatar.png'"
                            :alt="selectedAppointment.name"
                            class="object-cover border-2 border-surface-200"
                            style="width: 250px;"
                        />
                    </div>
                    <div class="flex flex-col gap-2 flex-1">
                        <div class="flex flex-col gap-1">
                            <label class="font-semibold text-surface-700 dark:text-surface-400 text-sm">Patient Name:</label>
                            <span class="text-surface-900 dark:text-surface-0 leading-normal">{{ selectedAppointment.name }}</span>
                        </div>
                        <div class="flex flex-col gap-1">
                            <label class="font-semibold text-surface-700 dark:text-surface-400 text-sm">Date & Time:</label>
                            <span class="text-surface-900 dark:text-surface-0 leading-normal">{{ selectedAppointment.date }} at {{ selectedAppointment.time }}</span>
                        </div>
                    </div>
                </div>

                <!-- Reason for Visit -->
                <div v-if="selectedAppointment.reason" class="flex flex-col gap-2">
                    <label class="font-semibold text-surface-700 dark:text-surface-400">Reason for Visit:</label>
                    <p class="text-surface-900 bg-surface-50 p-3 rounded border">{{ selectedAppointment.reason }}</p>
                </div>

                <div class="flex justify-end gap-3 mt-6 pt-4 border-t">
                    <Button  @click="confimrAcceptRequest($event)" label="Accept" icon="pi pi-check" severity="success"></Button>
                    <Button  @click="confirmRejectRequest($event)" label="Reject" icon="pi pi-times" severity="danger"></Button>
                    <Button label="View" icon="pi pi-eye" severity="info" outlined ></Button>
                </div>
            </div>
        </Dialog>
    </div>
</template>

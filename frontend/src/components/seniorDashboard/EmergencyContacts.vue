<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { Contacts as ContactService } from '@/service/ContactService';

const toast = useToast();
const contactList = ref([]);
const visible = ref(false);

const newContact = ref({
    Name: '',
    Mobileno: '',
    Email:'',
    Relationship: '',
});

onMounted(() => {
    contactList.value = ContactService.getContactsData();
});

const showAddContactOverlay = () => {
    visible.value = true;
};

const addContact = () => {
    if (newContact.value.Name && newContact.value.Mobileno && newContact.value.Relationship) {
        contactList.value.push({ ...newContact.value });
        toast.add({ severity: 'success', summary: 'Added', detail: 'Emergency Contact Added', life: 3000 });
        visible.value = false;
        newContact.value = { Name: '', Mobileno: '',Email:'', Relationship: '' };
    } else {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Please fill all fields', life: 3000 });
    }
};
</script>

<template>
    <Toast />
    <div class="card">
        <div class="flex items-center justify-between mb-4">
            <span class="text-xl font-bold">Emergency Contacts</span>
            <Button label="Add Contact" class="text-green-500 bg-green-100" @click="showAddContactOverlay" />
        </div>

        <DataTable :value="contactList" :rows="5" :paginator="true" v-if="contactList.length" responsiveLayout="scroll">
            <Column field="Name" header="Name"></Column>
            <Column field="Mobileno" header="Phone Number"></Column>
            <Column field="Email" header="Email"></Column>
            <Column field="Relationship" header="Relationship"></Column>
        </DataTable>
        <div v-else class="text-center text-gray-400">No contacts added yet.</div>

        <!-- Overlay Dialog -->
        <Dialog v-model:visible="visible" modal header="Add Emergency Contact" :style="{ width: '35rem' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
            <div class="flex flex-col gap-4">
                <label for="name" class="text-sm font-medium text-gray-700">Full Name</label>
                <InputText id="name" v-model="newContact.Name" class="w-full" />

                <label for="phone" class="text-sm font-medium text-gray-700">Phone Number</label>
                <InputText id="phone" v-model="newContact.Mobileno" class="w-full" />

                <label for="email_id" class="text-sm font-medium text-gray-700">Email</label>
                <InputText id="email_id" v-model="newContact.email_id" class="w-full" />

                <label for="relationship" class="text-sm font-medium text-gray-700">Relationship</label>
                <InputText id="relationship" v-model="newContact.Relationship" class="w-full" />

                <Button label="Save Contact" @click="addContact" class="w-full" />
            </div>
        </Dialog>

    </div>
</template>

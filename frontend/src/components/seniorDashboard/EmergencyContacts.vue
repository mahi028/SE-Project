<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { Contacts as ContactService } from '@/service/ContactService';

const toast = useToast();
const contactList = ref([]);
const visible = ref(false);
const submitted = ref(false);
const saving = ref(false);

const newContact = ref({
    Name: '',
    Mobileno: '',
    Email: '',
    Relationship: '',
});

const relationshipOptions = [
    { label: 'Spouse', value: 'Spouse' },
    { label: 'Son', value: 'Son' },
    { label: 'Daughter', value: 'Daughter' },
    { label: 'Son-in-law', value: 'Son-in-law' },
    { label: 'Daughter-in-law', value: 'Daughter-in-law' },
    { label: 'Brother', value: 'Brother' },
    { label: 'Sister', value: 'Sister' },
    { label: 'Friend', value: 'Friend' },
    { label: 'Neighbor', value: 'Neighbor' },
    { label: 'Doctor', value: 'Doctor' },
    { label: 'Caregiver', value: 'Caregiver' },
    { label: 'Other', value: 'Other' }
];

onMounted(() => {
    contactList.value = ContactService.getContactsData();
});

const showAddContactOverlay = () => {
    visible.value = true;
    submitted.value = false;
};

const cancelAdd = () => {
    visible.value = false;
    newContact.value = { Name: '', Mobileno: '', Email: '', Relationship: '' };
    submitted.value = false;
};

const addContact = async () => {
    submitted.value = true;

    if (newContact.value.Name && newContact.value.Mobileno && newContact.value.Relationship) {
        saving.value = true;
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 500));

            contactList.value.push({ ...newContact.value });
            toast.add({
                severity: 'success',
                summary: 'Contact Added',
                detail: `${newContact.value.Name} has been added to your emergency contacts`,
                life: 3000
            });
            cancelAdd();
        } catch (error) {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: 'Failed to add contact. Please try again.',
                life: 3000
            });
        } finally {
            saving.value = false;
        }
    } else {
        toast.add({
            severity: 'warn',
            summary: 'Missing Information',
            detail: 'Please fill in all required fields',
            life: 3000
        });
    }
};

const getRelationshipSeverity = (relationship) => {
    switch (relationship.toLowerCase()) {
        case 'spouse':
            return 'danger';
        case 'son':
        case 'daughter':
            return 'success';
        case 'doctor':
        case 'caregiver':
            return 'info';
        case 'friend':
        case 'neighbor':
            return 'warning';
        default:
            return 'secondary';
    }
};
</script>

<template>
    <Toast />
    <div class="emergency-contacts-card">
        <Card class="w-full">
            <template #header>
                <div class="section-header">
                    <i class="pi pi-phone text-red-500"></i>
                    <h3 class="section-title">Emergency Contacts</h3>
                </div>
            </template>
            <template #content>
                <div class="flex items-center justify-between mb-6">
                    <p class="text-surface-600 dark:text-surface-400">
                        Manage your emergency contacts for quick access during critical situations.
                    </p>
                    <Button
                        label="Add Contact"
                        icon="pi pi-plus"
                        severity="success"
                        outlined
                        @click="showAddContactOverlay"
                        class="flex-shrink-0"
                    />
                </div>

                <DataTable
                    v-if="contactList.length"
                    :value="contactList"
                    :rows="5"
                    :paginator="true"
                    responsiveLayout="scroll"
                    class="contact-table"
                >
                    <Column field="Name" header="Name" style="min-width: 150px">
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <Avatar
                                    :label="data.Name.charAt(0)"
                                    class="bg-blue-500 text-white"
                                    shape="circle"
                                    size="small"
                                />
                                <span class="font-medium text-surface-900 dark:text-surface-0">{{ data.Name }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column field="Mobileno" header="Phone Number" style="min-width: 140px">
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <i class="pi pi-phone text-green-500"></i>
                                <a :href="`tel:${data.Mobileno}`" class="text-blue-600 dark:text-blue-400 hover:underline">
                                    {{ data.Mobileno }}
                                </a>
                            </div>
                        </template>
                    </Column>
                    <Column field="Email" header="Email" style="min-width: 180px">
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <i class="pi pi-envelope text-blue-500"></i>
                                <a :href="`mailto:${data.Email}`" class="text-blue-600 dark:text-blue-400 hover:underline">
                                    {{ data.Email }}
                                </a>
                            </div>
                        </template>
                    </Column>
                    <Column field="Relationship" header="Relationship" style="min-width: 120px">
                        <template #body="{ data }">
                            <Tag
                                :value="data.Relationship"
                                :severity="getRelationshipSeverity(data.Relationship)"
                                class="text-sm"
                            />
                        </template>
                    </Column>
                </DataTable>

                <div v-else class="empty-state">
                    <div class="text-center py-12">
                        <div class="text-surface-400 dark:text-surface-500 mb-4">
                            <i class="pi pi-users text-6xl"></i>
                        </div>
                        <h4 class="text-xl font-medium text-surface-700 dark:text-surface-300 mb-2">
                            No Emergency Contacts Added
                        </h4>
                        <p class="text-surface-500 dark:text-surface-400 mb-4">
                            Add emergency contacts to ensure help is just a call away.
                        </p>
                        <Button
                            label="Add Your First Contact"
                            icon="pi pi-plus"
                            severity="success"
                            @click="showAddContactOverlay"
                        />
                    </div>
                </div>
            </template>
        </Card>

        <!-- Enhanced Dialog -->
        <Dialog
            v-model:visible="visible"
            modal
            header="Add Emergency Contact"
            :style="{ width: '500px' }"
            :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
            class="contact-dialog"
        >
            <template #header>
                <div class="dialog-header">
                    <i class="pi pi-user-plus text-green-500 mr-2"></i>
                    <span>Add Emergency Contact</span>
                </div>
            </template>

            <div class="dialog-content">
                <div class="grid formgrid p-fluid">
                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <InputText
                                id="contactName"
                                v-model="newContact.Name"
                                class="w-full"
                                :class="{'p-invalid': !newContact.Name && submitted}"
                            />
                            <label for="contactName">Full Name *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 md:col-6 mb-4 pr-md-2">
                        <FloatLabel>
                            <InputText
                                id="contactPhone"
                                v-model="newContact.Mobileno"
                                class="w-full"
                                :class="{'p-invalid': !newContact.Mobileno && submitted}"
                            />
                            <label for="contactPhone">Phone Number *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 md:col-6 mb-4 pl-md-2">
                        <FloatLabel>
                            <InputText
                                id="contactEmail"
                                v-model="newContact.Email"
                                type="email"
                                class="w-full"
                            />
                            <label for="contactEmail">Email Address</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <Select
                                id="contactRelationship"
                                v-model="newContact.Relationship"
                                :options="relationshipOptions"
                                optionLabel="label"
                                optionValue="value"
                                class="w-full"
                                :class="{'p-invalid': !newContact.Relationship && submitted}"
                            />
                            <label for="contactRelationship">Relationship *</label>
                        </FloatLabel>
                    </div>
                </div>

                <div class="info-section">
                    <div class="flex items-start gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                        <div class="text-sm text-blue-700 dark:text-blue-300">
                            <p class="font-medium mb-1">Emergency Contact Guidelines</p>
                            <ul class="space-y-1">
                                <li>• Choose someone who is easily reachable</li>
                                <li>• Ensure they are aware of your medical conditions</li>
                                <li>• Add multiple contacts for better coverage</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-3 mt-4">
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        outlined
                        @click="cancelAdd"
                        class="flex-shrink-0"
                    />
                    <Button
                        label="Save Contact"
                        icon="pi pi-check"
                        severity="success"
                        @click="addContact"
                        class="flex-shrink-0"
                        :loading="saving"
                    />
                </div>
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
.emergency-contacts-card {
    max-width: 100%;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem 1.5rem 0;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
}

.contact-table {
    border-radius: 8px;
    overflow: hidden;
}

.empty-state {
    background: var(--surface-ground);
    border-radius: 12px;
    border: 2px dashed var(--surface-border);
}

.dialog-header {
    display: flex;
    align-items: center;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
}

.dialog-content {
    padding: 1.5rem 0;
}

.info-section {
    margin-top: 2rem;
}

/* Enhanced spacing for form fields */
.field.mb-4 {
    margin-bottom: 1.5rem !important;
}

.pr-md-2 {
    padding-right: 0.5rem;
}

.pl-md-2 {
    padding-left: 0.5rem;
}

/* Responsive field spacing */
@media (max-width: 768px) {
    .pr-md-2,
    .pl-md-2 {
        padding-left: 0;
        padding-right: 0;
    }

    .field.mb-4 {
        margin-bottom: 1.25rem !important;
    }

    .dialog-content {
        padding: 1rem 0;
    }
}

/* Dark mode enhancements */
:global(.p-dark) .emergency-contacts-card :deep(.p-card) {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
}

:global(.p-dark) .dialog-header {
    color: var(--text-color);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .section-header {
        padding: 1rem 1rem 0;
        flex-direction: column;
        align-items: start;
        gap: 0.5rem;
    }
}

/* Animation enhancements */
.contact-table :deep(tr) {
    transition: all 0.3s ease;
}

.contact-table :deep(tr:hover) {
    background: var(--surface-hover);
}

:deep(.p-button) {
    transition: all 0.3s ease;
}

:deep(.p-button:hover) {
    transform: translateY(-1px);
}
</style>

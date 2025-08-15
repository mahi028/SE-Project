<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useQuery, useMutation } from '@vue/apollo-composable';
import gql from 'graphql-tag';

const toast = useToast();
const visible = ref(false);
const submitted = ref(false);
const saving = ref(false);
const editingContact = ref(null);

const newContact = ref({
    name: '',
    phoneNum: '',
    email: '',
    relationship: '',
    sendAlert: true
});

// GraphQL queries and mutations
const GET_EMERGENCY_CONTACTS = gql`
    query GetEmergencyContacts {
        getEmergencyContacts {
            contId
            senId
            name
            email
            phoneNum
            sendAlert
            relationship
        }
    }
`;

const ADD_EMERGENCY_CONTACT = gql`
    mutation AddEmergencyContact($name: String!, $email: String!, $phoneNum: String!, $relationship: String!, $sendAlert: Boolean!) {
        addEmergencyContact(
            name: $name
            email: $email
            phoneNum: $phoneNum
            relationship: $relationship
            sendAlert: $sendAlert
        ) {
            message
            status
        }
    }
`;

const UPDATE_EMERGENCY_CONTACT = gql`
    mutation UpdateEmergencyContact($contId: Int!, $name: String, $email: String, $phoneNum: String, $relationship: String, $sendAlert: Boolean) {
        updateEmergencyContact(
            contId: $contId
            name: $name
            email: $email
            phoneNum: $phoneNum
            relationship: $relationship
            sendAlert: $sendAlert
        ) {
            message
            status
        }
    }
`;

// Apollo composables
const { result, loading, error, refetch } = useQuery(GET_EMERGENCY_CONTACTS);
const { mutate: addEmergencyContact } = useMutation(ADD_EMERGENCY_CONTACT);
const { mutate: updateEmergencyContact } = useMutation(UPDATE_EMERGENCY_CONTACT);

// Computed property for contacts list
const contactList = computed(() => {
    return result.value?.getEmergencyContacts || [];
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

const showAddContactOverlay = () => {
    editingContact.value = null;
    newContact.value = {
        name: '',
        phoneNum: '',
        email: '',
        relationship: '',
        sendAlert: true
    };
    visible.value = true;
    submitted.value = false;
};

const showEditContactOverlay = (contact) => {
    editingContact.value = contact;
    newContact.value = {
        name: contact.name,
        phoneNum: contact.phoneNum,
        email: contact.email || '',
        relationship: contact.relationship,
        sendAlert: contact.sendAlert
    };
    visible.value = true;
    submitted.value = false;
};

const cancelAdd = () => {
    visible.value = false;
    editingContact.value = null;
    newContact.value = {
        name: '',
        phoneNum: '',
        email: '',
        relationship: '',
        sendAlert: true
    };
    submitted.value = false;
};

const validateForm = () => {
    return newContact.value.name &&
           newContact.value.phoneNum &&
           newContact.value.relationship;
};

const saveContact = async () => {
    submitted.value = true;

    if (!validateForm()) {
        toast.add({
            severity: 'warn',
            summary: 'Missing Information',
            detail: 'Please fill in all required fields',
            life: 3000
        });
        return;
    }

    saving.value = true;
    try {
        let result;

        if (editingContact.value) {
            // Update existing contact
            result = await updateEmergencyContact({
                contId: editingContact.value.contId,
                name: newContact.value.name,
                phoneNum: newContact.value.phoneNum,
                email: newContact.value.email || null,
                relationship: newContact.value.relationship,
                sendAlert: newContact.value.sendAlert
            });
        } else {
            // Add new contact
            result = await addEmergencyContact({
                name: newContact.value.name,
                phoneNum: newContact.value.phoneNum,
                email: newContact.value.email || '',
                relationship: newContact.value.relationship,
                sendAlert: newContact.value.sendAlert
            });
        }

        const response = result?.data?.addEmergencyContact || result?.data?.updateEmergencyContact;

        if (response?.status === 201 || response?.status === 200) {
            toast.add({
                severity: 'success',
                summary: editingContact.value ? 'Contact Updated' : 'Contact Added',
                detail: response.message || `${newContact.value.name} has been ${editingContact.value ? 'updated' : 'added'} successfully`,
                life: 3000
            });

            // Refetch contacts to update the list
            await refetch();
            cancelAdd();
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: response?.message || 'Failed to save contact. Please try again.',
                life: 3000
            });
        }
    } catch (error) {
        console.error('Error saving contact:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to save contact. Please try again.',
            life: 3000
        });
    } finally {
        saving.value = false;
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
                <!-- Loading state -->
                <div v-if="loading" class="text-center py-8">
                    <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                    <p class="mt-4">Loading contacts...</p>
                </div>

                <!-- Error state -->
                <div v-else-if="error" class="text-center py-8">
                    <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
                    <p class="text-red-600">Failed to load emergency contacts</p>
                    <Button label="Retry" @click="refetch" class="mt-3" />
                </div>

                <!-- Content -->
                <div v-else>
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
                        <Column field="name" header="Name" style="min-width: 150px">
                            <template #body="{ data }">
                                <div class="flex items-center gap-2">
                                    <Avatar
                                        :label="data.name.charAt(0)"
                                        class="bg-blue-500 text-white"
                                        shape="circle"
                                        size="small"
                                    />
                                    <span class="font-medium text-surface-900 dark:text-surface-0">{{ data.name }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column field="phoneNum" header="Phone Number" style="min-width: 140px">
                            <template #body="{ data }">
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-phone text-green-500"></i>
                                    <a :href="`tel:${data.phoneNum}`" class="text-blue-600 dark:text-blue-400 hover:underline">
                                        {{ data.phoneNum }}
                                    </a>
                                </div>
                            </template>
                        </Column>
                        <Column field="email" header="Email" style="min-width: 180px">
                            <template #body="{ data }">
                                <div v-if="data.email" class="flex items-center gap-2">
                                    <i class="pi pi-envelope text-blue-500"></i>
                                    <a :href="`mailto:${data.email}`" class="text-blue-600 dark:text-blue-400 hover:underline">
                                        {{ data.email }}
                                    </a>
                                </div>
                                <span v-else class="text-surface-400">-</span>
                            </template>
                        </Column>
                        <Column field="relationship" header="Relationship" style="min-width: 120px">
                            <template #body="{ data }">
                                <Tag
                                    :value="data.relationship"
                                    :severity="getRelationshipSeverity(data.relationship)"
                                    class="text-sm"
                                />
                            </template>
                        </Column>
                        <Column field="sendAlert" header="Alert" style="min-width: 80px">
                            <template #body="{ data }">
                                <div class="flex items-center gap-2">
                                    <i :class="data.sendAlert ? 'pi pi-check-circle text-green-500' : 'pi pi-times-circle text-red-500'"></i>
                                    <span class="text-sm">{{ data.sendAlert ? 'Yes' : 'No' }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column header="Actions" style="min-width: 100px">
                            <template #body="{ data }">
                                <div class="flex gap-2">
                                    <Button
                                        icon="pi pi-pencil"
                                        size="small"
                                        outlined
                                        @click="showEditContactOverlay(data)"
                                        v-tooltip.top="'Edit Contact'"
                                    />
                                </div>
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
                </div>
            </template>
        </Card>

        <!-- Enhanced Dialog -->
        <Dialog
            v-model:visible="visible"
            modal
            :header="editingContact ? 'Edit Emergency Contact' : 'Add Emergency Contact'"
            :style="{ width: '500px' }"
            :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
            class="contact-dialog"
        >
            <template #header>
                <div class="dialog-header">
                    <i :class="editingContact ? 'pi pi-user-edit text-blue-500' : 'pi pi-user-plus text-green-500'" class="mr-2"></i>
                    <span>{{ editingContact ? 'Edit Emergency Contact' : 'Add Emergency Contact' }}</span>
                </div>
            </template>

            <div class="dialog-content">
                <div class="grid formgrid p-fluid">
                    <div class="field col-12 mb-4">
                        <label for="contactName" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Full Name *</label>
                        <InputText
                            id="contactName"
                            v-model="newContact.name"
                            placeholder="Enter full name"
                            class="w-full"
                            :class="{'p-invalid': !newContact.name && submitted}"
                        />
                    </div>

                    <div class="field col-12 md:col-6 mb-4 pr-md-2">
                        <label for="contactPhone" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Phone Number *</label>
                        <InputText
                            id="contactPhone"
                            v-model="newContact.phoneNum"
                            placeholder="Enter phone number"
                            class="w-full"
                            :class="{'p-invalid': !newContact.phoneNum && submitted}"
                        />
                    </div>

                    <div class="field col-12 md:col-6 mb-4 pl-md-2">
                        <label for="contactEmail" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Email Address</label>
                        <InputText
                            id="contactEmail"
                            v-model="newContact.email"
                            type="email"
                            placeholder="Enter email address"
                            class="w-full"
                        />
                    </div>

                    <div class="field col-12 mb-4">
                        <label for="contactRelationship" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Relationship *</label>
                        <Select
                            id="contactRelationship"
                            v-model="newContact.relationship"
                            :options="relationshipOptions"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="Select relationship"
                            class="w-full"
                            :class="{'p-invalid': !newContact.relationship && submitted}"
                        />
                    </div>

                    <div class="field col-12 mb-4">
                        <div class="flex items-center gap-3">
                            <Checkbox
                                id="sendAlert"
                                v-model="newContact.sendAlert"
                                :binary="true"
                            />
                            <label for="sendAlert" class="text-sm">Send alerts to this contact</label>
                        </div>
                        <small class="text-surface-500 dark:text-surface-400 mt-1 block">
                            When enabled, this contact will receive emergency alerts and notifications.
                        </small>
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
                        :label="editingContact ? 'Update Contact' : 'Save Contact'"
                        icon="pi pi-check"
                        severity="success"
                        @click="saveContact"
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

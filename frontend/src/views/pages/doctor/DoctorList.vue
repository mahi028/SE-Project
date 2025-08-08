<script setup>
import { doctorService } from '@/service/DoctorService';
import { reviewService } from '@/service/ReviewService';
import { useLoginStore } from '@/store/loginStore';
import { onMounted, ref, computed } from 'vue';

const loginStore = useLoginStore();
const doctors = ref(null);
const options = ref(['list', 'grid']);
const layout = ref('grid');
const pincode = ref(loginStore.pincode);
const selectedSpecialization = ref(null);
const selectedRating = ref(null);
const selectedStatus = ref(null);

onMounted(() => {
    if (loginStore.role === 'mod') {
        // For moderators, get all doctors regardless of status
        doctorService.getAllDoctors().then((data) => {
            doctors.value = data
        });
    } else {
        // For regular users, get only approved doctors
        doctorService.getDoctorList(pincode.value).then((data) => {
            doctors.value = data;
        });
    }
});

const reFetchDoctors = () => {
    if (loginStore.role === 'mod') {
        doctorService.getAllDoctors().then((data) => {
            doctors.value = pincode.value ? data.filter(doctor => doctor.pincode === pincode.value) : data;
        });
    } else {
        doctorService.getDoctorList(pincode.value).then((data) => {
            doctors.value = data;
        });
    }
}

// Get unique specializations from current doctors list
const availableSpecializations = computed(() => {
    if (!doctors.value) return [];
    const specializations = [...new Set(doctors.value.map(doctor => doctor.specialization))];
    return specializations.map(spec => ({ label: spec, value: spec }));
});

// Rating filter options
const ratingOptions = [
    { label: '5 Stars', value: 5 },
    { label: '4+ Stars', value: 4 },
    { label: '3+ Stars', value: 3 },
    { label: '2+ Stars', value: 2 },
    { label: '1+ Stars', value: 1 }
];

// Status filter options (only for moderators)
const statusOptions = [
    { label: 'Approved', value: 1 },
    { label: 'Approval Pending', value: 0 },
    { label: 'Rejected', value: -1 },
    { label: 'Flagged', value: -2 }
];

// Filter doctors based on selected criteria
const filteredDoctors = computed(() => {
    if (!doctors.value) return [];

    let filtered = [...doctors.value];

    // Filter by specialization
    if (selectedSpecialization.value) {
        filtered = filtered.filter(doctor => doctor.specialization === selectedSpecialization.value);
    }

    // Filter by rating
    if (selectedRating.value) {
        filtered = filtered.filter(doctor => {
            const avgRating = parseFloat(reviewService.getAverageRating(doctor.ez_id));
            return avgRating >= selectedRating.value;
        });
    }

    // Filter by status (only for moderators)
    if (selectedStatus.value !== null && loginStore.role === 'mod') {
        filtered = filtered.filter(doctor => doctor.status === selectedStatus.value);
    }

    return filtered;
});

function getSpecializationColor(specialization) {
    switch (specialization) {
        case 'Cardiologist':
            return 'danger';
        case 'Neurologist':
            return 'success';
        case 'Pediatrician':
            return 'info';
        case 'Gynecologist':
            return 'warning';
        case 'Orthopedist':
            return 'secondary';
        default:
            return 'primary';
    }
}

function getAvailabilityColor(availability) {
    return availability.length >= 5 ? 'success' : 'warning';
}

function getStatusColor(status) {
    switch (status) {
        case 1:
            return 'success';
        case 0:
            return 'warning';
        case -1:
            return 'danger';
        case -2:
            return 'danger';
        default:
            return 'secondary';
    }
}

function getStatusLabel(status) {
    switch (status) {
        case 1:
            return 'Approved';
        case 0:
            return 'Pending';
        case -1:
            return 'Rejected';
        case -2:
            return 'Flagged';
        default:
            return 'Unknown';
    }
}

const clearSpecializationFilter = () => {
    selectedSpecialization.value = null;
}

const clearRatingFilter = () => {
    selectedRating.value = null;
}

const clearStatusFilter = () => {
    selectedStatus.value = null;
}

const clearAllFilters = () => {
    selectedSpecialization.value = null;
    selectedRating.value = null;
    selectedStatus.value = null;
}
</script>

<template>
  <div class="flex flex-col">
    <div class="card">
        <div class="font-semibold text-xl mb-4">Doctor Directory</div>
        <DataView :value="filteredDoctors" :layout="layout">
            <template #header>
                <div class="flex flex-col lg:flex-row m-3 gap-4 justify-between">
                    <!-- Filter Section -->
                    <div class="flex flex-col gap-4">
                        <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center flex-wrap">
                            <!-- Specialization Filter -->
                            <div class="flex gap-2">
                                <div class="flex flex-col">
                                    <label for="specialization" class="text-sm font-medium text-gray-700 mb-1">Specialization</label>
                                    <Select
                                        id="specialization"
                                        v-model="selectedSpecialization"
                                        :options="availableSpecializations"
                                        optionLabel="label"
                                        optionValue="value"
                                        placeholder="All Specializations"
                                        class="w-48"
                                        showClear
                                    />
                                </div>
                                <Button
                                    v-if="selectedSpecialization"
                                    icon="pi pi-times"
                                    @click="clearSpecializationFilter"
                                    outlined
                                    rounded
                                    size="small"
                                    v-tooltip.top="'Clear specialization filter'"
                                    class="self-end"
                                />
                            </div>

                            <!-- Rating Filter -->
                            <div class="flex gap-2">
                                <div class="flex flex-col">
                                    <label for="rating" class="text-sm font-medium text-gray-700 mb-1">Minimum Rating</label>
                                    <Select
                                        id="rating"
                                        v-model="selectedRating"
                                        :options="ratingOptions"
                                        optionLabel="label"
                                        optionValue="value"
                                        placeholder="All Ratings"
                                        class="w-36"
                                        showClear
                                    />
                                </div>
                                <Button
                                    v-if="selectedRating"
                                    icon="pi pi-times"
                                    @click="clearRatingFilter"
                                    outlined
                                    rounded
                                    size="small"
                                    v-tooltip.top="'Clear rating filter'"
                                    class="self-end"
                                />
                            </div>

                            <!-- Status Filter (Only for Moderators) -->
                            <div v-if="loginStore.role === 'mod'" class="flex gap-2">
                                <div class="flex flex-col">
                                    <label for="status" class="text-sm font-medium text-gray-700 mb-1">Status</label>
                                    <Select
                                        id="status"
                                        v-model="selectedStatus"
                                        :options="statusOptions"
                                        optionLabel="label"
                                        optionValue="value"
                                        placeholder="All Status"
                                        class="w-36"
                                        showClear
                                    />
                                </div>
                                <Button
                                    v-if="selectedStatus !== null"
                                    icon="pi pi-times"
                                    @click="clearStatusFilter"
                                    outlined
                                    rounded
                                    size="small"
                                    v-tooltip.top="'Clear status filter'"
                                    class="self-end"
                                />
                            </div>
                        </div>

                        <!-- Active Filters Display -->
                        <div v-if="selectedSpecialization || selectedRating || selectedStatus !== null" class="flex flex-wrap gap-2 items-center">
                            <span class="text-sm text-gray-600">Active filters:</span>
                            <Chip v-if="selectedSpecialization" :label="`Specialization: ${selectedSpecialization}`" removable @remove="clearSpecializationFilter" />
                            <Chip v-if="selectedRating" :label="`Rating: ${selectedRating}+ stars`" removable @remove="clearRatingFilter" />
                            <Chip v-if="selectedStatus !== null && loginStore.role === 'mod'" :label="`Status: ${getStatusLabel(selectedStatus)}`" removable @remove="clearStatusFilter" />
                            <Button label="Clear All" @click="clearAllFilters" text size="small" />
                        </div>

                        <!-- Results Count -->
                        <div class="text-sm text-gray-600">
                            Showing {{ filteredDoctors.length }} doctor(s)
                        </div>
                    </div>

                    <!-- Search and Layout Controls -->
                    <div class="flex gap-4 items-center">
                        <form class="flex gap-2" @submit.prevent="reFetchDoctors()">
                            <div class="flex flex-col">
                                <label for="over_label" class="text-sm font-medium text-gray-700 mb-1">Pincode</label>
                                <InputText id="over_label" v-model="pincode" placeholder="Enter pincode" />
                            </div>
                            <Button icon="pi pi-refresh" type="submit" rounded raised class="self-end"/>
                        </form>
                        <SelectButton v-model="layout" :options="options" :allowEmpty="false" class="self-end">
                            <template #option="{ option }">
                                <i :class="[option === 'list' ? 'pi pi-bars' : 'pi pi-table']" />
                            </template>
                        </SelectButton>
                    </div>
                </div>
            </template>
            <template #list="slotProps">
                <div class="flex flex-col">
                    <div v-for="(item, index) in slotProps.items" :key="index">
                        <div class="flex flex-col sm:flex-row sm:items-center p-6 gap-4" :class="{ 'border-t border-surface': index !== 0 }">
                            <div class="md:w-40 relative flex items-center justify-center bg-green-50 rounded p-4">
                                <img class="block xl:block mx-auto rounded w-full" src="/images/doctorIcon.avif" :alt="item.name" />
                                <Tag :value="item.specialization" :severity="getSpecializationColor(item.specialization)" class="absolute dark:!bg-surface-900" style="left: 4px; top: 4px"></Tag>
                                <Tag v-if="loginStore.role === 'mod'" :value="getStatusLabel(item.status)" :severity="getStatusColor(item.status)" class="absolute dark:!bg-surface-900" style="right: 4px; top: 4px"></Tag>
                            </div>
                            <div class="flex flex-col md:flex-row justify-between md:items-center flex-1 gap-6">
                                <div class="flex flex-col gap-2">
                                    <div>
                                        <div class="text-lg font-medium">{{ item.name }}</div>
                                        <span class="text-surface-500 dark:text-surface-400 text-sm">{{ item.specialization }}</span>
                                        <div class="text-xs text-surface-400 mt-1">{{ item.qualification }}</div>
                                        <div class="flex items-center gap-1 mt-1">
                                            <Rating :modelValue="parseFloat(reviewService.getAverageRating(item.ez_id))" readonly :cancel="false" :stars="5" class="text-xs" />
                                            <span class="text-xs text-gray-600">({{ reviewService.getAverageRating(item.ez_id) }})</span>
                                        </div>
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <div class="flex items-center gap-2">
                                            <i class="pi pi-building text-surface-400"></i>
                                            <span class="text-sm">{{ item.hospital }}</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <i class="pi pi-map-marker text-surface-400"></i>
                                            <span class="text-sm">{{ item.address }}</span>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <i class="pi pi-phone text-surface-400"></i>
                                            <span class="text-sm">{{ item.phone }}</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="flex flex-col md:items-end gap-4">
                                    <div class="flex items-center gap-2">
                                        <span class="text-lg font-semibold text-green-600">{{ item.consultation_fee }}</span>
                                        <div class="text-xs text-surface-500">{{ item.experience }}</div>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <i class="pi pi-clock text-surface-400"></i>
                                        <span class="text-sm">{{ item.timings }}</span>
                                    </div>
                                    <div class="flex flex-wrap gap-1">
                                        <Chip v-for="day in item.availability.slice(0, 3)" :key="day" :label="day.substring(0, 3)" class="text-xs" />
                                        <Chip v-if="item.availability.length > 3" :label="`+${item.availability.length - 3}`" class="text-xs" severity="secondary" />
                                    </div>
                                    <div class="flex gap-2">
                                        <a :href="`tel:${item.phone}`">
                                            <Button icon="pi pi-phone" outlined size="small"></Button>
                                        </a>
                                        <Button icon="pi pi-calendar" label="View" size="small" class="flex-auto md:flex-initial whitespace-nowrap" as="router-link" :to="`/doctor/${item.ez_id}`"></Button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>

            <template #grid="slotProps">
                <div class="grid grid-cols-12 gap-4">
                    <div v-for="(item, index) in slotProps.items" :key="index" class="col-span-12 sm:col-span-6 lg:col-span-3 p-2">
                        <div class="p-6 border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-900 rounded flex flex-col h-full">
                            <div class="bg-green-50 flex justify-center rounded p-6 relative">
                                <img class="block xl:block mx-auto rounded w-full" src="/images/doctorIcon.avif" :alt="item.name" />
                                <Tag :value="item.specialization" :severity="getSpecializationColor(item.specialization)" class="absolute dark:!bg-surface-900" style="left: 8px; top: 8px"></Tag>
                                <Tag v-if="loginStore.role === 'mod'" :value="getStatusLabel(item.status)" :severity="getStatusColor(item.status)" class="absolute dark:!bg-surface-900" style="right: 8px; top: 8px"></Tag>
                            </div>
                            <div class="pt-6 flex-1 flex flex-col">
                                <div class="flex flex-col gap-2 flex-1">
                                    <div>
                                        <div class="text-lg font-medium">{{ item.name }}</div>
                                        <span class="text-surface-500 dark:text-surface-400 text-sm">{{ item.specialization }}</span>
                                        <div class="text-xs text-surface-400 mt-1">{{ item.qualification }}</div>
                                        <div class="flex items-center gap-1 mt-1">
                                            <Rating :modelValue="parseFloat(reviewService.getAverageRating(item.ez_id))" readonly :cancel="false" :stars="5" class="text-xs" />
                                            <span class="text-xs text-gray-600">({{ reviewService.getAverageRating(item.ez_id) }})</span>
                                        </div>
                                    </div>
                                    <div class="flex items-center gap-2 mt-2">
                                        <i class="pi pi-building text-surface-400"></i>
                                        <span class="text-sm">{{ item.hospital }}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <i class="pi pi-map-marker text-surface-400"></i>
                                        <span class="text-sm">{{ item.address.split(',')[0] }}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <i class="pi pi-phone text-surface-400"></i>
                                        <span class="text-sm">{{ item.phone }}</span>
                                    </div>
                                    <div class="flex items-center justify-between mt-3">
                                        <span class="text-lg font-semibold text-green-600">{{ item.consultation_fee }}</span>
                                        <span class="text-xs text-surface-500">{{ item.experience }}</span>
                                    </div>
                                    <div class="flex items-center gap-2 mt-2">
                                        <i class="pi pi-clock text-surface-400"></i>
                                        <span class="text-xs">{{ item.timings }}</span>
                                    </div>
                                    <div class="flex flex-wrap gap-1 mt-3">
                                        <Chip v-for="day in item.availability.slice(0, 4)" :key="day" :label="day.substring(0, 3)" class="text-xs" />
                                        <Chip v-if="item.availability.length > 4" :label="`+${item.availability.length - 4}`" class="text-xs" severity="secondary" />
                                    </div>
                                </div>
                                <div class="flex gap-2 mt-6">
                                    <Button icon="pi pi-calendar" label="View" size="small" class="flex-auto whitespace-nowrap" as="router-link" :to="`/doctor/${item.ez_id}`"></Button>
                                    <a :href="`tel:${item.phone}`">
                                        <Button icon="pi pi-phone" outlined size="small"></Button>
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
        </DataView>
    </div>
  </div>
</template>

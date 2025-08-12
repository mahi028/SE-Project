<script setup>
import { useLoginStore } from '@/store/loginStore';
import { onMounted, ref, computed, watch } from 'vue';
import { useQuery } from '@vue/apollo-composable';
import gql from 'graphql-tag';

const loginStore = useLoginStore();
const layout = ref('grid');
const options = ref(['list', 'grid']);
// Initialize pincode from loginStore
const pincode = ref(loginStore.pincode || '');
const selectedSpecialization = ref(null);
const selectedRating = ref(null);
const selectedStatus = ref(null);

// GraphQL Queries
const GET_DOCTORS_QUERY = gql`
    query GetDoctors($pincode: String, $specialization: String, $status: Int, $includeAllStatus: Boolean) {
        getDoctors(pincode: $pincode, specialization: $specialization, status: $status, includeAllStatus: $includeAllStatus) {
            docId
            ezId
            gender
            address
            pincode
            alternatePhoneNum
            licenseNumber
            specialization
            affiliation
            qualification
            experience
            consultationFee
            workingHours
            availability
            availabilityStatus
            appointmentWindow
            user {
                name
                email
                phoneNum
                profileImageUrl
            }
            docReviews {
                reviewId
                rating
                review
            }
        }
    }
`;

const GET_ALL_DOCTORS_QUERY = gql`
    query GetAllDoctors {
        getAllDoctors {
            docId
            ezId
            gender
            address
            pincode
            alternatePhoneNum
            licenseNumber
            specialization
            affiliation
            qualification
            experience
            consultationFee
            workingHours
            availability
            availabilityStatus
            appointmentWindow
            user {
                name
                email
                phoneNum
                profileImageUrl
            }
            docReviews {
                reviewId
                rating
                review
            }
        }
    }
`;

// Determine which query to use based on user role
const isModeratorView = computed(() => loginStore.role === 2);
const queryVariables = computed(() => {
    if (isModeratorView.value) {
        return {
            pincode: pincode.value || null,
            specialization: selectedSpecialization.value || null,
            status: selectedStatus.value,
            includeAllStatus: true
        };
    } else {
        return {
            pincode: pincode.value || null,
            specialization: selectedSpecialization.value || null,
            includeAllStatus: false
        };
    }
});

// Use the appropriate query based on user role
const { result, loading, error, refetch } = useQuery(
    isModeratorView.value ? GET_ALL_DOCTORS_QUERY : GET_DOCTORS_QUERY,
    queryVariables,
    // {
    //     fetchPolicy: 'cache-and-network'
    // }
);

// Process doctors data
const doctors = computed(() => {
    const rawDoctors = isModeratorView.value
        ? result.value?.getAllDoctors
        : result.value?.getDoctors;

    if (!rawDoctors) return [];

    return rawDoctors.map(doctor => {
        // Parse affiliation
        let affiliation = {};
        try {
            affiliation = typeof doctor.affiliation === 'string'
                ? JSON.parse(doctor.affiliation)
                : (doctor.affiliation || {});
        } catch (e) {
            console.error('Error parsing affiliation:', e);
        }

        // Parse qualification
        let qualifications = [];
        try {
            qualifications = typeof doctor.qualification === 'string'
                ? JSON.parse(doctor.qualification)
                : (Array.isArray(doctor.qualification) ? doctor.qualification : []);
        } catch (e) {
            console.error('Error parsing qualification:', e);
        }

        // Parse availability
        let availability = [];
        try {
            availability = typeof doctor.availability === 'string'
                ? JSON.parse(doctor.availability)
                : (Array.isArray(doctor.availability) ? doctor.availability : []);
        } catch (e) {
            console.error('Error parsing availability:', e);
        }

        // Calculate average rating
        const avgRating = getAverageRating(doctor.docReviews || []);

        return {
            ez_id: doctor.ezId,
            docId: doctor.docId,
            name: doctor.user?.name || 'Unknown Doctor',
            email: doctor.user?.email,
            phone: doctor.user?.phoneNum,
            alternatePhone: doctor.alternatePhoneNum,
            specialization: doctor.specialization || 'General Medicine',
            licenseNumber: doctor.licenseNumber,
            experience: doctor.experience ? `${doctor.experience} years` : 'Not specified',
            consultation_fee: doctor.consultationFee ? `₹${doctor.consultationFee}` : 'Not specified',
            hospital: affiliation.name || 'Not specified',
            address: doctor.address || 'Address not provided',
            pincode: doctor.pincode,
            timings: doctor.workingHours || 'Not specified',
            availability: availability,
            qualification: qualifications.map(q => `${q.name} (${q.year})`).join(', ') || 'Not specified',
            status: doctor.availabilityStatus,
            appointmentWindow: doctor.appointmentWindow || 30,
            averageRating: avgRating,
            reviewCount: doctor.docReviews?.length || 0,
            profileImage: doctor.user?.profileImageUrl
        };
    });
});

// Helper function to calculate average rating
const getAverageRating = (reviews) => {
    if (!reviews || reviews.length === 0) return '0.0';
    const sum = reviews.reduce((acc, review) => acc + (parseFloat(review.rating) || 0), 0);
    return (sum / reviews.length).toFixed(1);
};

// Get unique specializations from current doctors list
const availableSpecializations = computed(() => {
    if (!doctors.value) return [];
    const specializations = [...new Set(doctors.value.map(doctor => doctor.specialization))];
    return specializations
        .filter(spec => spec && spec !== 'Not specified')
        .map(spec => ({ label: spec, value: spec }));
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

    // Filter by rating (client-side as GraphQL doesn't handle this)
    if (selectedRating.value) {
        filtered = filtered.filter(doctor => {
            const avgRating = parseFloat(doctor.averageRating);
            return avgRating >= selectedRating.value;
        });
    }

    return filtered;
});

const reFetchDoctors = async () => {
    try {
        await refetch(queryVariables.value);
    } catch (error) {
        console.error('Error refetching doctors:', error);
    }
};

// Watch for changes in filter values and refetch - but debounce pincode input
watch([selectedSpecialization, selectedStatus], () => {
    reFetchDoctors();
}, { deep: true });

// Manual refetch function for pincode
const refetchWithPincode = async () => {
    try {
        await refetch(queryVariables.value);
    } catch (error) {
        console.error('Error refetching doctors:', error);
    }
};

function getSpecializationColor(specialization) {
    const colors = {
        'Cardiology': 'danger',
        'Cardiologist': 'danger',
        'Neurology': 'success',
        'Neurologist': 'success',
        'Pediatrics': 'info',
        'Pediatrician': 'info',
        'Gynecology': 'warning',
        'Gynecologist': 'warning',
        'Orthopedics': 'secondary',
        'Orthopedist': 'secondary',
        'General Medicine': 'primary'
    };
    return colors[specialization] || 'primary';
}

function getStatusColor(status) {
    switch (status) {
        case 1: return 'success';
        case 0: return 'warning';
        case -1: return 'danger';
        case -2: return 'danger';
        default: return 'secondary';
    }
}

function getStatusLabel(status) {
    switch (status) {
        case 1: return 'Approved';
        case 0: return 'Pending';
        case -1: return 'Rejected';
        case -2: return 'Flagged';
        default: return 'Unknown';
    }
}

const clearSpecializationFilter = () => {
    selectedSpecialization.value = null;
};

const clearRatingFilter = () => {
    selectedRating.value = null;
};

const clearStatusFilter = () => {
    selectedStatus.value = null;
};

const clearAllFilters = () => {
    selectedSpecialization.value = null;
    selectedRating.value = null;
    selectedStatus.value = null;
    pincode.value = '';
    reFetchDoctors();
};

onMounted(() => {
    // Initial data is loaded automatically by useQuery
    // Set pincode from loginStore if available
    if (loginStore.pincode && !pincode.value) {
        pincode.value = loginStore.pincode;
    }
});
</script>

<template>
    <div class="flex flex-col">
        <div class="card">
            <div class="font-semibold text-xl mb-4">Doctor Directory</div>

            <!-- Loading state -->
            <div v-if="loading" class="text-center py-8">
                <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                <p class="mt-4">Loading doctors...</p>
            </div>

            <!-- Error state -->
            <div v-else-if="error" class="text-center py-8">
                <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
                <p class="text-red-600">Failed to load doctors</p>
                <Button label="Retry" @click="reFetchDoctors" class="mt-3" />
            </div>

            <!-- Content -->
            <DataView v-else :value="filteredDoctors" :layout="layout">
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
                                <div v-if="isModeratorView" class="flex gap-2">
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
                            <div v-if="selectedSpecialization || selectedRating || selectedStatus !== null || pincode" class="flex flex-wrap gap-2 items-center">
                                <span class="text-sm text-gray-600">Active filters:</span>
                                <Chip v-if="selectedSpecialization" :label="`Specialization: ${selectedSpecialization}`" removable @remove="clearSpecializationFilter" />
                                <Chip v-if="selectedRating" :label="`Rating: ${selectedRating}+ stars`" removable @remove="clearRatingFilter" />
                                <Chip v-if="selectedStatus !== null && isModeratorView" :label="`Status: ${getStatusLabel(selectedStatus)}`" removable @remove="clearStatusFilter" />
                                <Chip v-if="pincode" :label="`Pincode: ${pincode}`" removable @remove="() => { pincode = ''; refetchWithPincode(); }" />
                                <Button label="Clear All" @click="clearAllFilters" text size="small" />
                            </div>

                            <!-- Results Count -->
                            <div class="text-sm text-gray-600">
                                Showing {{ filteredDoctors.length }} doctor(s)
                            </div>
                        </div>

                        <!-- Search and Layout Controls -->
                        <div class="flex gap-4 items-center">
                            <form class="flex gap-2" @submit.prevent="refetchWithPincode">
                                <div class="flex flex-col">
                                    <label for="pincodeInput" class="text-sm font-medium text-gray-700 mb-1">Pincode</label>
                                    <InputText
                                        id="pincodeInput"
                                        v-model="pincode"
                                        placeholder="Enter pincode and press Enter"
                                        :class="{ 'border-blue-300': pincode }"
                                        @keyup.enter="refetchWithPincode"
                                    />
                                    <small v-if="pincode" class="text-xs text-blue-600 mt-1">
                                        Press Enter to search by pincode: {{ pincode }}
                                    </small>
                                </div>
                                <Button
                                    icon="pi pi-search"
                                    type="submit"
                                    rounded
                                    raised
                                    class="self-end"
                                    :loading="loading"
                                    v-tooltip.top="'Search by pincode'"
                                />
                            </form>
                            <SelectButton v-model="layout" :options="options" :allowEmpty="false" class="self-end">
                                <template #option="{ option }">
                                    <i :class="[option === 'list' ? 'pi pi-bars' : 'pi pi-table']" />
                                </template>
                            </SelectButton>
                        </div>
                    </div>
                </template>

                <!-- List Layout -->
                <template #list="slotProps">
                    <div class="flex flex-col">
                        <div v-for="(item, index) in slotProps.items" :key="index">
                            <div class="flex flex-col sm:flex-row sm:items-center p-6 gap-4" :class="{ 'border-t border-surface': index !== 0 }">
                                <div class="md:w-40 relative flex items-center justify-center bg-green-50 rounded p-4">
                                    <img class="block xl:block mx-auto rounded w-full" src="/images/doctorIcon.avif" :alt="item.name" />
                                    <Tag :value="item.specialization" :severity="getSpecializationColor(item.specialization)" class="absolute dark:!bg-surface-900" style="left: 4px; top: 4px"></Tag>
                                    <Tag v-if="isModeratorView" :value="getStatusLabel(item.status)" :severity="getStatusColor(item.status)" class="absolute dark:!bg-surface-900" style="right: 4px; top: 4px"></Tag>
                                </div>
                                <div class="flex flex-col md:flex-row justify-between md:items-center flex-1 gap-6">
                                    <div class="flex flex-col gap-2">
                                        <div>
                                            <div class="text-lg font-medium">{{ item.name }}</div>
                                            <span class="text-surface-500 dark:text-surface-400 text-sm">{{ item.specialization }}</span>
                                            <div class="text-xs text-surface-400 mt-1">{{ item.qualification }}</div>
                                            <div class="flex items-center gap-1 mt-1">
                                                <Rating :modelValue="parseFloat(item.averageRating)" readonly :cancel="false" :stars="5" class="text-xs" />
                                                <span class="text-xs text-gray-600">({{ item.averageRating }})</span>
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

                <!-- Grid Layout -->
                <template #grid="slotProps">
                    <div class="grid grid-cols-12 gap-4">
                        <div v-for="(item, index) in slotProps.items" :key="index" class="col-span-12 sm:col-span-6 lg:col-span-3 p-2">
                            <div class="p-6 border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-900 rounded flex flex-col h-full">
                                <div class="bg-green-50 flex justify-center rounded p-6 relative">
                                    <img class="block xl:block mx-auto rounded w-full" src="/images/doctorIcon.avif" :alt="item.name" />
                                    <Tag :value="item.specialization" :severity="getSpecializationColor(item.specialization)" class="absolute dark:!bg-surface-900" style="left: 8px; top: 8px"></Tag>
                                    <Tag v-if="isModeratorView" :value="getStatusLabel(item.status)" :severity="getStatusColor(item.status)" class="absolute dark:!bg-surface-900" style="right: 8px; top: 8px"></Tag>
                                </div>
                                <div class="pt-6 flex-1 flex flex-col">
                                    <div class="flex flex-col gap-2 flex-1">
                                        <div>
                                            <div class="text-lg font-medium">{{ item.name }}</div>
                                            <span class="text-surface-500 dark:text-surface-400 text-sm">{{ item.specialization }}</span>
                                            <div class="text-xs text-surface-400 mt-1">{{ item.qualification }}</div>
                                            <div class="flex items-center gap-1 mt-1">
                                                <Rating :modelValue="parseFloat(item.averageRating)" readonly :cancel="false" :stars="5" class="text-xs" />
                                                <span class="text-xs text-gray-600">({{ item.averageRating }})</span>
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

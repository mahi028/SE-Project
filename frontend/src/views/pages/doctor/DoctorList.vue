<script setup>
import { doctorService } from '@/service/DoctorService';
import { onMounted, ref } from 'vue';

const doctors = ref(null);
const options = ref(['list', 'grid']);
const layout = ref('list');
const pincode = ref('201010')

onMounted(() => {
    doctorService.getDoctorList(pincode.value).then((data) => {
        doctors.value = data
    });
});

const reFetchDoctors = ()=>{
    doctorService.getDoctorList(pincode.value).then((data) => {
        doctors.value = data
    });
}

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
</script>
<template>
  <div class="flex flex-col">
    <div class="card">
        <div class="font-semibold text-xl">Doctor Directory</div>
        <DataView :value="doctors" :layout="layout">
            <template #header>
                <div class="flex m-3 gap-4 justify-end">
                    <form class="flex" @submit.prevent="reFetchDoctors()">
                        <FloatLabel>
                            <InputText id="over_label" v-model="pincode" />
                            <label for="over_label">Pincode</label>
                        </FloatLabel>
                            <Button icon="pi pi-refresh" type="submit" rounded raised/>
                    </form>
                    <SelectButton v-model="layout" :options="options" :allowEmpty="false">
                        <template #option="{ option }">
                            <i :class="[option === 'list' ? 'pi pi-bars' : 'pi pi-table']" />
                        </template>
                    </SelectButton>
                </div>
            </template>
            <template #list="slotProps">
                <div class="flex flex-col">
                    <div v-for="(item, index) in slotProps.items" :key="index">
                        <div class="flex flex-col sm:flex-row sm:items-center p-6 gap-4" :class="{ 'border-t border-surface': index !== 0 }">
                            <div class="md:w-40 relative flex items-center justify-center bg-green-50 rounded p-4">
                                <img class="block xl:block mx-auto rounded w-full" src="/images/doctorIcon.avif" :alt="item.name" />
                                <Tag :value="item.specialization" :severity="getSpecializationColor(item.specialization)" class="absolute dark:!bg-surface-900" style="left: 4px; top: 4px"></Tag>
                            </div>
                            <div class="flex flex-col md:flex-row justify-between md:items-center flex-1 gap-6">
                                <div class="flex flex-col gap-2">
                                    <div>
                                        <div class="text-lg font-medium">{{ item.name }}</div>
                                        <span class="text-surface-500 dark:text-surface-400 text-sm">{{ item.specialization }}</span>
                                        <div class="text-xs text-surface-400 mt-1">{{ item.qualification }}</div>
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
                            </div>
                            <div class="pt-6 flex-1 flex flex-col">
                                <div class="flex flex-col gap-2 flex-1">
                                    <div>
                                        <div class="text-lg font-medium">{{ item.name }}</div>
                                        <span class="text-surface-500 dark:text-surface-400 text-sm">{{ item.specialization }}</span>
                                        <div class="text-xs text-surface-400 mt-1">{{ item.qualification }}</div>
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

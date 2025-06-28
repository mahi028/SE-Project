<script setup>
import { hospitalService } from '@/service/HospitalService';
import { onMounted, ref } from 'vue';

const hospitals = ref(null);
const options = ref(['list', 'grid']);
const layout = ref('list');
const pincode = ref('201010')

// get data from google places api
// async function getData() {
//     const url = "https://places.googleapis.com/v1/places:searchNearby";
//     const jsoni = {
//         "includedTypes": ["hospitals"],
//         "maxResultCount": 10,
//         "locationRestriction": {
//             "circle": {
//             "center": {
//                 "latitude": 37.7937,
//                 "longitude": -122.3965},
//             "radius": 500.0
//             }
//         }
//     }
//     try {
//         const response = await fetch(url, {
//             method: "POST",
//             body: JSON.stringify(jsoni),
//             header: JSON.stringify(
//                 {"X-Goog-Api-Key": "API_KEY"},
//                 {"X-Goog-FieldMask": "places.displayName"},
//             )
//         });
//         if (!response.ok) {
//         throw new Error(`Response status: ${response.status}`);
//         }

//         const json = await response.json();
//         console.log(json);
//     } catch (error) {
//         console.error(error.message);
//     }
// }

onMounted(() => {
    hospitalService.getHospitalList(pincode.value).then((data) => {
        hospitals.value = data
    });
    // getData()
});

const reFetchHospitals = ()=>{
    hospitalService.getHospitalList(pincode.value).then((data) => {
        hospitals.value = data
    });
}

function getTypeColor(type) {
    switch (type) {
        case 'Super-specialty':
            return 'success';
        case 'Multi-specialty':
            return 'info';
        case 'Clinic':
            return 'warning';
        default:
            return 'secondary';
    }
}

function getTimingsColor(timings) {
    return timings === '24/7' ? 'success' : 'info';
}
</script>
<template>
  <div class="flex flex-col">
    <div class="card">
        <div class="font-semibold text-xl">Hospital Directory</div>
        <DataView :value="hospitals" :layout="layout">
            <template #header>
                <div class="flex m-3 gap-4 justify-end">
                    <form class="flex" @submit.prevent="reFetchHospitals()">
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
                            <div class="md:w-40 relative flex items-center justify-center bg-blue-50 rounded p-4">
                                <img class="block xl:block mx-auto rounded w-full" src="/images/hospitalIcon.jpg" :alt="item.name" />
                                <Tag :value="item.type" :severity="getTypeColor(item.type)" class="absolute dark:!bg-surface-900" style="left: 4px; top: 4px"></Tag>
                            </div>
                            <div class="flex flex-col md:flex-row justify-between md:items-center flex-1 gap-6">
                                <div class="flex flex-col gap-2">
                                    <div>
                                        <div class="text-lg font-medium">{{ item.name }}</div>
                                        <span class="text-surface-500 dark:text-surface-400 text-sm">{{ item.type }}</span>
                                    </div>
                                    <div class="flex flex-col gap-1">
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
                                        <Tag :value="item.timings" :severity="getTimingsColor(item.timings)" />
                                        <span class="text-sm text-surface-500">{{ item.beds }} beds</span>
                                    </div>
                                    <div class="flex flex-wrap gap-1">
                                        <Chip v-for="service in item.services.slice(0, 3)" :key="service" :label="service" class="text-xs" />
                                        <Chip v-if="item.services.length > 3" :label="`+${item.services.length - 3} more`" class="text-xs" severity="secondary" />
                                    </div>
                                    <div class="flex gap-2">
                                        <Button icon="pi pi-phone" outlined size="small"></Button>
                                        <Button icon="pi pi-directions" label="Directions" size="small" class="flex-auto md:flex-initial whitespace-nowrap"></Button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </template>

            <template #grid="slotProps">
                <div class="grid grid-cols-12 gap-4">
                    <div v-for="(item, index) in slotProps.items" :key="index" class="col-span-12 sm:col-span-6 lg:col-span-4 p-2">
                        <div class="p-6 border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-900 rounded flex flex-col h-full">
                            <div class="bg-blue-50 flex justify-center rounded p-6 relative">
                                <img class="block xl:block mx-auto rounded w-full" src="/images/hospitalIcon.jpg" :alt="item.name" />
                                <Tag :value="item.type" :severity="getTypeColor(item.type)" class="absolute dark:!bg-surface-900" style="left: 8px; top: 8px"></Tag>
                            </div>
                            <div class="pt-6 flex-1 flex flex-col">
                                <div class="flex flex-col gap-2 flex-1">
                                    <div>
                                        <div class="text-lg font-medium">{{ item.name }}</div>
                                        <span class="text-surface-500 dark:text-surface-400 text-sm">{{ item.type }}</span>
                                    </div>
                                    <div class="flex items-center gap-2 mt-2">
                                        <i class="pi pi-map-marker text-surface-400"></i>
                                        <span class="text-sm">{{ item.address}}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <i class="pi pi-phone text-surface-400"></i>
                                        <span class="text-sm">{{ item.phone }}</span>
                                    </div>
                                    <div class="flex items-center justify-between mt-3">
                                        <Tag :value="item.timings" :severity="getTimingsColor(item.timings)" />
                                        <span class="text-sm text-surface-500">{{ item.beds }} beds</span>
                                    </div>
                                    <div class="flex flex-wrap gap-1 mt-3">
                                        <Chip v-for="service in item.services.slice(0, 2)" :key="service" :label="service" class="text-xs" />
                                        <Chip v-if="item.services.length > 2" :label="`+${item.services.length - 2}`" class="text-xs" severity="secondary" />
                                    </div>
                                </div>
                                <div class="flex gap-2 mt-6">
                                    <Button icon="pi pi-directions" label="Directions" size="small" class="flex-auto whitespace-nowrap"></Button>
                                    <Button icon="pi pi-phone" outlined size="small"></Button>
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

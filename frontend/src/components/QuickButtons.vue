<script setup>
    import { ref } from 'vue';
    import { RouterLink } from 'vue-router';
    import { useToast } from "primevue/usetoast";

    const props = defineProps({
        page: String,
    })

    const toast = useToast();

    const overlay = ref({
        'patient-lookup': false,
        'example-images': false,
        'SOS-overlay': false,
    })

    const lookupOptions = ref(['Email', 'EZID', 'Face']);
    const lookupValue = ref('Email');
    const lookupData = ref({
        email: '',
        ezid: '',
        face: '',
    })

    const onAdvancedUpload = () => {
        toast.add({ severity: 'info', summary: 'Success', detail: 'File Uploaded', life: 3000 });
    };

    const doctorWidgets = ref([
        {
            id: 1,
            label: 'Patient Lookup',
            desc: 'Find Patients info from Email, EZID or just their Face.',
            iconClass: 'pi pi-camera',
            action: 'overlay',
            type: 'patient-lookup',
        },
    ])

    const seniorWidgets = ref([
        {
            id: 1,
            label: 'Health Professionals',
            desc: 'Find and book appointments with health professionals.',
            iconClass: 'pi pi-user text-blue-500 !text-xl',
            action: 'redirect',
            redirect: '/doctor',
        },
        {
            id: 2,
            label: 'Hospitals',
            desc: 'Find all the hospitals in your area.',
            iconClass: 'pi pi-building text-blue-500 !text-xl',
            action: 'redirect',
            redirect: '/hospital',
        },
        {
            id: 3,
            label: 'SOS',
            desc: 'Only click this in case of serious Emergencies',
            iconClass: 'pi pi-phone',
            action: 'overlay',
            type: 'SOS-overlay',
        },
    ])

    const closeAllOverlays = ()=>{
        for (const key in overlay.value) {
                overlay.value[key] = false
            }
    }

    const toggleOverlay = (type, closeAll=true)=>{
        if (closeAll){
            closeAllOverlays()
        }
        if (type in overlay.value) {
            overlay.value[type] = true
        }
    }

    const sendSOS = ()=>{
        toast.add({ severity: 'success', summary: 'Success', detail: 'SOS Send Successfully.', life: 3000 });
        closeAllOverlays()
    }

</script>
<template>
    <Toast />
    <div class="col-span-12 lg:col-span-6 xl:col-span-3" v-for="widget in props.page == 'doctor' ? doctorWidgets : seniorWidgets" key="id">
        <RouterLink v-if="widget.action=='redirect'" :to="widget.redirect">
        <div class="card mb-0" >
                <div class="flex justify-between mb-4">
                    <div>
                        <span class="block font-medium text-xl mb-4">{{ widget.label }}</span>
                    </div>
                    <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                        <i :class="widget.iconClass"></i>
                    </div>
                </div>
                <span class="text-muted-color">{{ widget.desc }}</span>
            </div>
        </RouterLink>
        <button v-else-if="widget.action=='overlay'" @click="toggleOverlay(widget.type)" >
            <div class="card mb-0" :style="widget.label === 'SOS' ? 'background-color: #ef4444; color: white;' : ''" >
                <div class="flex justify-between mb-4">
                    <div>
                        <span class="block font-medium text-xl mb-4">{{ widget.label }}</span>
                    </div>
                    <div class="flex items-center justify-center rounded-border" :class="widget.label === 'SOS' ? 'bg-red-600' : 'bg-blue-100 dark:bg-blue-400/10'" style="width: 2.5rem; height: 2.5rem">
                        <i :class="widget.iconClass"></i>
                    </div>
                </div>
                <span :class="widget.label === 'SOS' ? 'text-red-100' : 'text-muted-color'">{{ widget.desc }}</span>
            </div>
        </button>
    </div>
    <div class="col-span-12 lg:col-span-6 xl:col-span-3" v-for="fakeItem in props.page == 'doctor' ? doctorWidgets.length % 4 : seniorWidgets.length % 4"></div>

    <!-- Overlays -->
        <!-- Patient Lookup -->
        <Dialog v-model:visible="overlay['patient-lookup']" modal header="Get Patient's Medical Info" :style="{ width: '35rem' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
            <div>
                <div class=" flex justify-center">
                    <SelectButton v-model="lookupValue" :options="lookupOptions" />
                </div>
                <label for="email" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2" v-show="lookupValue=='Email'">Email</label>
                <InputText id="email" type="text" placeholder="Email address" class="w-full md:w-[30rem] mb-8" v-model="lookupData.email" v-show="lookupValue=='Email'"/>

                <label for="ezid" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2" v-show="lookupValue=='EZID'">EZ ID</label>
                <InputText id="ezid" type="text" placeholder="Enter EZID" class="w-full md:w-[30rem] mb-8" v-model="lookupData.ezid" v-show="lookupValue=='EZID'"/>

                <div class="card" v-show="lookupValue=='Face'">
                    <FileUpload name="demo[]" url="/api/upload" @upload="onAdvancedUpload($event)" accept="image/*" :maxFileSize="1000000">
                        <template #empty>
                            <span>Drag and drop files to here to upload.</span>
                        </template>
                    </FileUpload>
                </div>
                <Button label="Get Info" class="w-full" as="router-link"></Button>
            </div>

            <br>
            <div class="flex items-center justify-center" v-show="lookupValue=='Face'">
                <Button type="button" @click="toggleOverlay('example-images', false)" variant="Text" label="See Example Images" severity="secondary"></Button>
            </div>
        </Dialog>

        <!-- Example Images -->
        <Dialog v-model:visible="overlay['example-images']" modal header="Example Images" :style="{ width: '45rem' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
            <div class="flex justify-evenly items-start">
                <div class="flex-shrink-0">
                    <img
                        src="https://www.wockhardthospitals.com/wp-content/uploads/2023/05/shutterstock_365746949-scaled_11zon.webp"
                        alt="ExampleImage1"
                        class="object-cover border-2 border-surface-200"
                        style="width: 250px;"
                    />
                </div>
                <div class="flex-shrink-0">
                    <img
                        src="https://www.wockhardthospitals.com/wp-content/uploads/2023/05/shutterstock_365746949-scaled_11zon.webp"
                        alt="ExampleImage1"
                        class="object-cover border-2 border-surface-200"
                        style="width: 250px;"
                    />
                </div>
            </div>
            <br>
            <div>
                <span class="block font-medium text-xl mb-4">Note</span>
                <p class="m-0">
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
                </p>
            </div>
            <br>
        </Dialog>

        <!-- SOS Overlay -->
        <Dialog v-model:visible="overlay['SOS-overlay']" modal header="SOS | Emergency" :style="{ width: '35rem', background: 'red', border: 'none', color: 'white'}" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
            <div class="flex flex-col items-center w-full gap-4 border-b border-surface-200 dark:border-surface-700">
                <i class="pi pi-exclamation-circle !text-6xl text-primary-500"></i>
                <p>Clicking this button will Notify all the Emergency contacts you have defined.</p>
                <p>Are you sure you want to continue?</p>
            </div>
            <br>
            <div class="flex justify-center">
                <Button @click="sendSOS()" label="Continue"></Button>
            </div>
        </Dialog>
</template>

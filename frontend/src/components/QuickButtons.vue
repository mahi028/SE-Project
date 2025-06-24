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
            action: 'overlay',
            type: 'patient-lookup',
        },
    ])

    const seniorWidgets = ref([
        {
            id: 1,
            label: '1st ',
            desc: 'lorem ipsum dolar sit emmet.',
            iconClass: 'pi pi-camera text-blue-500 !text-xl',
            action: 'redirect',
            redirect: '#',
        },
        {
            id: 2,
            label: '2nd',
            desc: 'lorem ipsum dolar sit emmet.',
            iconClass: 'pi pi-camera text-blue-500 !text-xl',
            action: 'redirect',
            redirect: '#',
        },
    ])

    const toggleOverlay = (type, closeAll=true)=>{
        if (closeAll){
            for (const key in overlay.value) {
                overlay.value[key] = false
            }
        }
        if (type in overlay.value) {
            overlay.value[type] = true
        }
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
        <div class="card mb-0" v-else-if="widget.action=='overlay'">
            <div class="flex justify-between mb-4">
                <div>
                    <span class="block font-medium text-xl mb-4">{{ widget.label }}</span>
                </div>
                <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                    <Button type="button" @click="toggleOverlay(widget.type)" icon="pi pi-search" rounded></Button>
                </div>
            </div>
            <span class="text-muted-color">{{ widget.desc }}</span>
        </div>
    </div>
    <div class="col-span-12 lg:col-span-6 xl:col-span-3" v-for="fakeItem in props.page == 'doctor' ? doctorWidgets.length % 4 : seniorWidgets.length % 4"></div>

    <!-- Patient Lookup -->
    <Dialog v-model:visible="overlay['patient-lookup']" modal header="Get Patient's Medical Info" :style="{ width: '35rem' }" closeOnEscape="true" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
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
</template>

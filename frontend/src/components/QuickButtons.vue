<script setup>
    import { ref } from 'vue';
    import { RouterLink } from 'vue-router';
    import { useToast } from "primevue/usetoast";
    import { useRouter } from 'vue-router';
    import { useLazyQuery } from '@vue/apollo-composable';
    import gql from 'graphql-tag';

    const router = useRouter()
    const props = defineProps({
        page: String,
    })

    const toast = useToast();

    // GraphQL query for user lookup
    const GET_USER_BY_CRITERIA = gql`
        query GetUser($ezId: String!) {
            getUser(ezId: $ezId) {
                ezId
                role
                name
                email
                senInfo {
                    senId
                    ezId
                }
                docInfo {
                    docId
                    ezId
                }
            }
        }
    `;

    const GET_USER_BY_EMAIL = gql`
        query GetUserByEmail($email: String!) {
            getUserByEmail(email: $email) {
                ezId
                role
                name
                email
                senInfo {
                    senId
                    ezId
                }
                docInfo {
                    docId
                    ezId
                }
            }
        }
    `;

    // Fix the lazy query hooks
    const { load: loadUserByEzId } = useLazyQuery(GET_USER_BY_CRITERIA);
    const { load: loadUserByEmail } = useLazyQuery(GET_USER_BY_EMAIL);

    const overlay = ref({
        'patient-lookup': false,
        'example-images': false,
        'user-lookup': false,
        'SOS-overlay': false,
    })

    const lookupOptions = ref(['Email', 'EZID', 'Face']);
    const lookupValue = ref('Email');
    const lookupData = ref({
        email: '',
        ezid: '',
        face: '',
    })
    const userlookupOptions = ref(['Email', 'EZID']);
    const userlookupValue = ref('Email');
    const userlookupData = ref({
        email: '',
        ezid: '',
    })
    const onAdvancedUpload = () => {
        toast.add({ severity: 'info', summary: 'Success', detail: 'File Uploaded', life: 3000 });
    };

    const getInfo = async () => {
        try {
            let result = null;

            if (lookupValue.value === 'Email') {
                if (!lookupData.value.email.trim()) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Missing Information',
                        detail: 'Please enter an email address.',
                        life: 3000
                    });
                    return;
                }

                result = await loadUserByEmail(GET_USER_BY_EMAIL, { email: lookupData.value.email });
            } else if (lookupValue.value === 'EZID') {
                if (!lookupData.value.ezid.trim()) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Missing Information',
                        detail: 'Please enter an EZ ID.',
                        life: 3000
                    });
                    return;
                }

                result = await loadUserByEzId(GET_USER_BY_CRITERIA, { ezId: lookupData.value.ezid });
            }

            // Fix the data extraction - useLazyQuery returns result in different structure
            let userData = null;
            if (result) {
                if (lookupValue.value === 'Email') {
                    userData = result.getUserByEmail;
                } else if (lookupValue.value === 'EZID') {
                    userData = result.getUser;
                }
            }

            if (userData) {
                // Check if user is a senior (role 0) and has senior info
                if (userData.role === 0 && userData.senInfo) {
                    router.push(`/senior/${userData.ezId}`);
                } else if (userData.role === 0) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Incomplete Profile',
                        detail: 'This senior citizen has not completed their registration.',
                        life: 3000
                    });
                } else {
                    toast.add({
                        severity: 'info',
                        summary: 'Not a Senior',
                        detail: 'This user is not a senior citizen. Use User Lookup for other user types.',
                        life: 3000
                    });
                }
            } else {
                toast.add({
                    severity: 'error',
                    summary: 'No User Found',
                    detail: 'Please check the information and try again.',
                    life: 3000
                });
            }
        } catch (error) {
            console.error('Error looking up patient:', error);
            toast.add({
                severity: 'error',
                summary: 'Lookup Failed',
                detail: 'Failed to lookup patient information. Please try again.',
                life: 3000
            });
        }
    };

    const getUserInfo = async () => {
        try {
            let result = null;

            if (userlookupValue.value === 'Email') {
                if (!userlookupData.value.email.trim()) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Missing Information',
                        detail: 'Please enter an email address.',
                        life: 3000
                    });
                    return;
                }

                result = await loadUserByEmail(GET_USER_BY_EMAIL, { email: userlookupData.value.email });
            } else if (userlookupValue.value === 'EZID') {
                if (!userlookupData.value.ezid.trim()) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Missing Information',
                        detail: 'Please enter an EZ ID.',
                        life: 3000
                    });
                    return;
                }

                result = await loadUserByEzId(GET_USER_BY_CRITERIA, { ezId: userlookupData.value.ezid });
            }

            // Fix the data extraction - useLazyQuery returns result in different structure
            let userData = null;
            if (result) {
                if (userlookupValue.value === 'Email') {
                    userData = result.getUserByEmail;
                } else if (userlookupValue.value === 'EZID') {
                    userData = result.getUser;
                }
            }

            if (userData) {
                // Route based on user role
                if (userData.role === 1 && userData.docInfo) {
                    // Doctor with complete profile
                    router.push(`/doctor/${userData.ezId}`);
                } else if (userData.role === 0 && userData.senInfo) {
                    // Senior with complete profile
                    router.push(`/senior/${userData.ezId}`);
                } else if (userData.role === 1) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Incomplete Profile',
                        detail: 'This doctor has not completed their registration.',
                        life: 3000
                    });
                } else if (userData.role === 0) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Incomplete Profile',
                        detail: 'This senior citizen has not completed their registration.',
                        life: 3000
                    });
                } else {
                    toast.add({
                        severity: 'info',
                        summary: 'User Found',
                        detail: `User found: ${userData.name} (Role: ${userData.role === 2 ? 'Moderator' : 'Unknown'})`,
                        life: 3000
                    });
                }
            } else {
                toast.add({
                    severity: 'error',
                    summary: 'No User Found',
                    detail: 'Please check the information and try again.',
                    life: 3000
                });
            }
        } catch (error) {
            console.error('Error looking up user:', error);
            toast.add({
                severity: 'error',
                summary: 'Lookup Failed',
                detail: 'Failed to lookup user information. Please try again.',
                life: 3000
            });
        }
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
    const modWidgets = ref([
        {
            id: 1,
            label: 'Health Professionals',
            desc: 'Find health professionals.',
            iconClass: 'pi pi-user text-blue-500 !text-xl',
            action: 'redirect',
            redirect: '/doctor',
        },
        {
            id: 2,
            label: 'User Lookup',
            desc: 'Search for User info from Email, EZID.',
            iconClass: 'pi pi-search',
            action: 'overlay',
            type: 'user-lookup',
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
    <div class="col-span-12 lg:col-span-6 xl:col-span-3"
        v-for="widget in {
            'senior': seniorWidgets,
            'doctor': doctorWidgets,
            'mod': modWidgets,
        }[props.page]"
        key="id"
    >
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
                <Button label="Get Info" @click="getInfo()" class="w-full"></Button>
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

        <!-- User Lookup -->
        <Dialog v-model:visible="overlay['user-lookup']" modal header="User Lookup" :style="{ width: '35rem' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
            <div>
                <div class=" flex justify-center">
                    <SelectButton v-model="userlookupValue" :options="userlookupOptions" />
                </div>
                <label for="user-email" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2" v-show="userlookupValue=='Email'">Email</label>
                <InputText id="user-email" type="text" placeholder="Email address" class="w-full md:w-[30rem] mb-8" v-model="userlookupData.email" v-show="userlookupValue=='Email'"/>

                <label for="user-ezid" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2" v-show="userlookupValue=='EZID'">EZ ID</label>
                <InputText id="user-ezid" type="text" placeholder="Enter EZID" class="w-full md:w-[30rem] mb-8" v-model="userlookupData.ezid" v-show="userlookupValue=='EZID'"/>

                <Button label="Get Info" @click="getUserInfo()" class="w-full"></Button>
            </div>
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

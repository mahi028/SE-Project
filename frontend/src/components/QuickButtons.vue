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

    // Face recognition variables and functions
    const recognitionResults = ref([]);
    const recognitionLoading = ref(false);
    const selectedPhoto = ref(null);

    const onPhotoSelect = (event) => {
        const files = event.files || event.target.files;
        if (files && files.length > 0) {
            selectedPhoto.value = files[0];
            // Clear previous results
            recognitionResults.value = [];
        }
    };

    const recognizeFace = async () => {
        if (!selectedPhoto.value) {
            toast.add({
                severity: 'warn',
                summary: 'No Photo Selected',
                detail: 'Please select a photo first.',
                life: 3000
            });
            return;
        }

        recognitionLoading.value = true;
        recognitionResults.value = [];

        try {
            const formData = new FormData();
            formData.append('photo', selectedPhoto.value);

            const response = await fetch('http://localhost:5000/user-lookup/recognize', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('EZCARE-LOGIN-TOKEN')}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.matches) {
                recognitionResults.value = data.matches;

                if (data.matches.length > 0) {
                    toast.add({
                        severity: 'success',
                        summary: 'Face Recognition Successful',
                        detail: `Found ${data.matches.length} potential match(es)`,
                        life: 4000
                    });
                } else {
                    toast.add({
                        severity: 'info',
                        summary: 'No Matches Found',
                        detail: 'No matching faces found in the database.',
                        life: 3000
                    });
                }
            } else {
                // Handle different error cases
                if (response.status === 404) {
                    toast.add({
                        severity: 'warn',
                        summary: 'No Match Found',
                        detail: data.message || 'No matching user found',
                        life: 4000
                    });

                    // Show debug info if available
                    if (data.debug_info) {
                        console.log('Recognition Debug Info:', data.debug_info);
                    }
                } else {
                    toast.add({
                        severity: 'error',
                        summary: 'Recognition Failed',
                        detail: data.error || 'Failed to recognize face',
                        life: 3000
                    });
                }
            }
        } catch (error) {
            console.error('Face recognition error:', error);
            toast.add({
                severity: 'error',
                summary: 'Network Error',
                detail: 'Failed to connect to recognition service',
                life: 3000
            });
        } finally {
            recognitionLoading.value = false;
        }
    };

    const clearRecognitionResults = () => {
        recognitionResults.value = [];
        selectedPhoto.value = null;
    };

    const viewProfile = async (ezId) => {
        try {
            // First get user info to determine their role
            const result = await loadUserByEzId(GET_USER_BY_CRITERIA, { ezId });
            const userData = result?.getUser;

            if (userData) {
                // Route based on user role
                if (userData.role === 0 && userData.senInfo) {
                    router.push(`/senior/${userData.ezId}`);
                } else if (userData.role === 1 && userData.docInfo) {
                    router.push(`/doctor/${userData.ezId}`);
                } else if (userData.role === 0) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Incomplete Profile',
                        detail: 'This senior citizen has not completed their registration.',
                        life: 3000
                    });
                } else if (userData.role === 1) {
                    toast.add({
                        severity: 'warn',
                        summary: 'Incomplete Profile',
                        detail: 'This doctor has not completed their registration.',
                        life: 3000
                    });
                } else {
                    toast.add({
                        severity: 'info',
                        summary: 'Profile Found',
                        detail: `User: ${userData.name} (${userData.role === 2 ? 'Moderator' : 'Unknown Role'})`,
                        life: 3000
                    });
                }

                // Close the overlay after successful navigation
                closeAllOverlays();
            } else {
                toast.add({
                    severity: 'error',
                    summary: 'Profile Error',
                    detail: 'Could not load user profile details',
                    life: 3000
                });
            }
        } catch (error) {
            console.error('Error viewing profile:', error);
            toast.add({
                severity: 'error',
                summary: 'Profile Load Failed',
                detail: 'Failed to load user profile',
                life: 3000
            });
        }
    };

    const getConfidenceColor = (confidence) => {
        switch (confidence.toLowerCase()) {
            case 'very high':
                return 'success';
            case 'high':
                return 'success';
            case 'medium':
                return 'warning';
            case 'low':
                return 'danger';
            default:
                return 'secondary';
        }
    };

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
        <Dialog v-model:visible="overlay['patient-lookup']" modal header="Get Patient's Medical Info" :style="{ width: '40rem' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
            <div>
                <div class="flex justify-center mb-4">
                    <SelectButton v-model="lookupValue" :options="lookupOptions" />
                </div>

                <!-- Email Input -->
                <template v-if="lookupValue === 'Email'">
                    <label for="email" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Email</label>
                    <InputText id="email" type="text" placeholder="Email address" class="w-full mb-4" v-model="lookupData.email"/>
                    <Button label="Get Info" @click="getInfo()" class="w-full" />
                </template>

                <!-- EZID Input -->
                <template v-if="lookupValue === 'EZID'">
                    <label for="ezid" class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">EZ ID</label>
                    <InputText id="ezid" type="text" placeholder="Enter EZID" class="w-full mb-4" v-model="lookupData.ezid"/>
                    <Button label="Get Info" @click="getInfo()" class="w-full" />
                </template>

                <!-- Face Recognition -->
                <template v-if="lookupValue === 'Face'">
                    <div class="mb-4">
                        <label class="block text-surface-900 dark:text-surface-0 text-xl font-medium mb-2">Upload Patient Photo</label>
                        <div class="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
                            <input
                                type="file"
                                ref="fileInput"
                                accept="image/*"
                                @change="onPhotoSelect"
                                class="hidden"
                                id="photoInput"
                            />
                            <label for="photoInput" class="cursor-pointer">
                                <div class="flex flex-col items-center gap-3">
                                    <i class="pi pi-camera text-4xl text-surface-400 hover:text-primary-500 transition-colors"></i>
                                    <div>
                                        <p class="text-surface-700 dark:text-surface-300 font-medium">
                                            {{ selectedPhoto ? 'Photo Selected' : 'Click to select patient photo' }}
                                        </p>
                                        <small class="text-surface-500 dark:text-surface-400">
                                            Supported formats: JPG, PNG (Max: 5MB)
                                        </small>
                                    </div>
                                </div>
                            </label>
                        </div>
                    </div>

                    <!-- Selected Photo Preview -->
                    <div v-if="selectedPhoto" class="mb-4 p-4 bg-surface-50 dark:bg-surface-800 rounded-lg">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <i class="pi pi-image text-primary-500"></i>
                                <div>
                                    <p class="font-medium text-surface-900 dark:text-surface-0">{{ selectedPhoto.name }}</p>
                                    <small class="text-surface-500 dark:text-surface-400">
                                        {{ (selectedPhoto.size / 1024 / 1024).toFixed(2) }} MB
                                    </small>
                                </div>
                            </div>
                            <Button
                                icon="pi pi-times"
                                size="small"
                                outlined
                                severity="secondary"
                                @click="clearRecognitionResults"
                                v-tooltip.top="'Remove photo'"
                            />
                        </div>
                    </div>

                    <!-- Recognition Button -->
                    <Button
                        label="Recognize Face"
                        icon="pi pi-search"
                        @click="recognizeFace()"
                        class="w-full mb-4"
                        :loading="recognitionLoading"
                        :disabled="!selectedPhoto"
                        severity="primary"
                    />

                    <!-- Recognition Results -->
                    <div v-if="recognitionResults.length > 0" class="mt-4">
                        <Divider />
                        <h4 class="text-lg font-semibold mb-3 flex items-center gap-2">
                            <i class="pi pi-check-circle text-green-500"></i>
                            Recognition Results ({{ recognitionResults.length }})
                        </h4>
                        
                        <div class="space-y-3">
                            <Card v-for="(result, index) in recognitionResults" :key="index" class="p-3">
                                <template #content>
                                    <div class="flex items-center justify-between">
                                        <div class="flex-1">
                                            <div class="flex items-center gap-3 mb-2">
                                                <Avatar 
                                                    :label="result.ezId ? result.ezId.slice(-2) : 'U'" 
                                                    class="bg-primary-500 text-white" 
                                                    size="normal"
                                                />
                                                <div>
                                                    <p class="font-semibold text-lg">{{ result.ezId || 'Unknown ID' }}</p>
                                                    <div class="flex items-center gap-2">
                                                        <Tag 
                                                            :value="result.confidence || 'Unknown'" 
                                                            :severity="getConfidenceColor(result.confidence)"
                                                            class="text-sm"
                                                        />
                                                        <span class="text-sm text-surface-600">{{ result.match_percentage || '0%' }} match</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <Button 
                                            label="View Profile" 
                                            icon="pi pi-user"
                                            size="small"
                                            @click="viewProfile(result.ezId)"
                                            class="flex-shrink-0"
                                            :disabled="!result.ezId"
                                        />
                                    </div>
                                </template>
                            </Card>
                        </div>

                        <!-- Results Info -->
                        <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                            <div class="flex items-start gap-2">
                                <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                                <div class="text-sm text-blue-700 dark:text-blue-300">
                                    <p class="font-medium">Recognition Tips:</p>
                                    <ul class="mt-1 space-y-1">
                                        <li>• Higher confidence matches are more likely to be correct</li>
                                        <li>• Multiple matches may indicate similar facial features</li>
                                        <li>• Verify identity through other means when confidence is low</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- No Results Message -->
                    <div v-else-if="recognitionResults.length === 0 && selectedPhoto && !recognitionLoading" class="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                        <div class="flex items-center gap-2 text-yellow-700 dark:text-yellow-300">
                            <i class="pi pi-exclamation-triangle"></i>
                            <span class="text-sm">No matching faces found. Try with a clearer photo or use Email/EZID lookup.</span>
                        </div>
                    </div>
                </template>

                <!-- Example Images Button -->
                <div class="flex items-center justify-center mt-4" v-if="lookupValue === 'Face'">
                    <Button
                        type="button"
                        @click="toggleOverlay('example-images', false)"
                        label="See Example Images"
                        severity="secondary"
                        outlined
                        size="small"
                    />
                </div>
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

<style scoped>
/* Add custom styles for better recognition results display */
.recognition-results {
    max-height: 400px;
    overflow-y: auto;
}

.confidence-high {
    background: linear-gradient(135deg, #22c55e, #16a34a);
}

.confidence-medium {
    background: linear-gradient(135deg, #f59e0b, #d97706);
}

.confidence-low {
    background: linear-gradient(135deg, #ef4444, #dc2626);
}

/* Custom file input styling */
#photoInput {
    display: none;
}

.file-drop-zone {
    transition: all 0.3s ease;
}

.file-drop-zone:hover {
    border-color: var(--primary-500);
    background-color: var(--primary-50);
}

:global(.p-dark) .file-drop-zone:hover {
    background-color: var(--primary-900);
}

/* Selected photo preview styling */
.photo-preview {
    border: 1px solid var(--surface-border);
    background: var(--surface-ground);
}

:global(.p-dark) .photo-preview {
    background: var(--surface-800);
    border-color: var(--surface-700);
}
</style>

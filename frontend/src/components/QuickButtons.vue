<script setup>
    import { ref } from 'vue';
    import { RouterLink } from 'vue-router';
    import { useToast } from "primevue/usetoast";
    import { useRouter } from 'vue-router';
    import { useLazyQuery, useMutation } from '@vue/apollo-composable';
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

    const SOS_MUTATION = gql`
        mutation SOS {
            sos {
                message
                status
            }
        }
    `;

    const { mutate: triggerSOS, loading: sosLoading } = useMutation(SOS_MUTATION);

    const overlay = ref({
        'patient-lookup': false,
        'example-images': false,
        'user-lookup': false,
        'SOS-overlay': false,
        'add-embeddings-overlay': false,
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
            label: 'Register Face ID',
            desc: 'Add your facial video for easy profile lookups during emergencies',
            iconClass: 'pi pi-video text-green-500 !text-xl',
            action: 'overlay',
            type: 'add-embeddings-overlay',
        },
        {
            id: 4,
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

    const sendSOS = async () => {
        try {
            const { data } = await triggerSOS();
            const response = data?.sos;

            if (response?.status === 200) {
                toast.add({
                    severity: 'success',
                    summary: 'SOS Alert Sent',
                    detail: response.message || 'Emergency alert has been sent to your contacts',
                    life: 5000
                });
            } else {
                toast.add({
                    severity: 'error',
                    summary: 'SOS Failed',
                    detail: response?.message || 'Failed to send emergency alert',
                    life: 5000
                });
            }
        } catch (error) {
            console.error('SOS Error:', error);
            toast.add({
                severity: 'error',
                summary: 'SOS Failed',
                detail: 'An error occurred while sending the emergency alert. Please try again or contact emergency services directly.',
                life: 5000
            });
        } finally {
            closeAllOverlays();
        }
    }

    // Face recognition variables and functions
    const recognitionResults = ref([]);
    const recognitionLoading = ref(false);
    const selectedPhoto = ref(null);
    const hasAttemptedRecognition = ref(false); // Add this new flag

    const onPhotoSelect = (event) => {
        const files = event.files || event.target.files;
        if (files && files.length > 0) {
            selectedPhoto.value = files[0];
            // Clear previous results and reset recognition attempt flag
            recognitionResults.value = [];
            hasAttemptedRecognition.value = false;
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
        hasAttemptedRecognition.value = true; // Set flag when recognition is attempted

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
        hasAttemptedRecognition.value = false; // Reset flag when clearing
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

    // Add facial embeddings registration variables
    const embeddingsVideo = ref(null);
    const embeddingsUploading = ref(false);

    const onEmbeddingsVideoSelect = (event) => {
        const files = event.files || event.target.files;
        if (files && files.length > 0) {
            embeddingsVideo.value = files[0];
        }
    };

    const clearEmbeddingsVideo = () => {
        embeddingsVideo.value = null;
    };

    const registerFaceEmbeddings = async () => {
        if (!embeddingsVideo.value) {
            toast.add({
                severity: 'warn',
                summary: 'No Video Selected',
                detail: 'Please select a video file first.',
                life: 3000
            });
            return;
        }

        // Validate video file
        if (!embeddingsVideo.value.type.startsWith('video/')) {
            toast.add({
                severity: 'error',
                summary: 'Invalid File Type',
                detail: 'Please select a valid video file.',
                life: 3000
            });
            return;
        }

        // Check file size (limit to 50MB)
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (embeddingsVideo.value.size > maxSize) {
            toast.add({
                severity: 'error',
                summary: 'File Too Large',
                detail: 'Video file must be less than 50MB.',
                life: 3000
            });
            return;
        }

        embeddingsUploading.value = true;

        try {
            const formData = new FormData();
            formData.append('video', embeddingsVideo.value);

            const response = await fetch('http://localhost:5000/user-lookup/register', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('EZCARE-LOGIN-TOKEN')}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                toast.add({
                    severity: 'success',
                    summary: 'Registration Successful',
                    detail: data.message || `Face ID registered successfully with ${data.total_embeddings} face embeddings!`,
                    life: 5000
                });

                // Clear form and close overlay
                clearEmbeddingsVideo();
                closeAllOverlays();
            } else {
                toast.add({
                    severity: 'error',
                    summary: 'Registration Failed',
                    detail: data.error || 'Failed to register face ID',
                    life: 4000
                });
            }
        } catch (error) {
            console.error('Face ID registration error:', error);
            toast.add({
                severity: 'error',
                summary: 'Network Error',
                detail: 'Failed to connect to the registration service. Please try again.',
                life: 4000
            });
        } finally {
            embeddingsUploading.value = false;
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
        <Dialog
        v-model:visible="overlay['patient-lookup']"
        modal
        :style="{ width: '70rem' }"
        :breakpoints="{ '1199px': '90vw', '575px': '95vw' }"
        class="enhanced-lookup-dialog"
    >
        <template #header>
            <div class="enhanced-dialog-header">
                <div class="header-icon-wrapper bg-blue-500">
                    <i class="pi pi-search text-white text-2xl"></i>
                </div>
                <div class="header-content">
                    <h2 class="header-title">Patient Medical Information</h2>
                    <p class="header-subtitle">Find and access patient records securely using multiple search methods</p>
                </div>
                <div class="header-decoration">
                    <div class="decoration-dot bg-blue-500"></div>
                    <div class="decoration-dot bg-blue-400"></div>
                    <div class="decoration-dot bg-blue-300"></div>
                </div>
            </div>
        </template>

        <div class="enhanced-dialog-content">
            <!-- Search Method Tabs -->
            <div class="search-method-section">
                <div class="section-header">
                    <i class="pi pi-sliders-h text-primary-500 text-lg"></i>
                    <h3 class="section-title">Choose Search Method</h3>
                </div>
                <div class="method-tabs">
                    <div
                        v-for="option in lookupOptions"
                        :key="option"
                        :class="['method-tab', { 'active': lookupValue === option }]"
                        @click="lookupValue = option"
                    >
                        <div class="tab-icon">
                            <i :class="option === 'Email' ? 'pi pi-envelope' :
                                      option === 'EZID' ? 'pi pi-id-card' : 'pi pi-camera'"></i>
                        </div>
                        <div class="tab-content">
                            <span class="tab-label">{{ option }}</span>
                            <small class="tab-description">
                                {{ option === 'Email' ? 'Search by email address' :
                                   option === 'EZID' ? 'Search by unique ID' : 'Facial recognition' }}
                            </small>
                        </div>
                        <div v-if="lookupValue === option" class="tab-indicator"></div>
                    </div>
                </div>
            </div>

            <!-- Email Search -->
            <div v-if="lookupValue === 'Email'" class="search-content-section">
                <div class="search-card email-search">
                    <div class="search-card-header">
                        <div class="search-icon bg-green-100 text-green-600">
                            <i class="pi pi-envelope"></i>
                        </div>
                        <div class="search-info">
                            <h4>Email Search</h4>
                            <p>Search patient by their registered email address</p>
                        </div>
                    </div>

                    <div class="search-form">
                        <div class="form-group">
                            <label for="email" class="form-label">Patient Email Address</label>
                            <div class="input-with-icon">
                                <i class="pi pi-envelope input-icon"></i>
                                <InputText
                                    id="email"
                                    v-model="lookupData.email"
                                    placeholder="Enter patient's email address"
                                    class="enhanced-input"
                                />
                            </div>
                        </div>

                        <Button
                            label="Search Patient"
                            icon="pi pi-search"
                            @click="getInfo()"
                            class="search-btn primary"
                            style="color: green !important;"
                            :disabled="!lookupData.email.trim()"
                        />
                    </div>
                </div>
            </div>

            <!-- EZID Search -->
            <div v-if="lookupValue === 'EZID'" class="search-content-section">
                <div class="search-card ezid-search">
                    <div class="search-card-header">
                        <div class="search-icon bg-purple-100 text-purple-600">
                            <i class="pi pi-id-card"></i>
                        </div>
                        <div class="search-info">
                            <h4>EZ ID Search</h4>
                            <p>Search patient by their unique EZ ID</p>
                        </div>
                    </div>

                    <div class="search-form">
                        <div class="form-group">
                            <label for="ezid" class="form-label">Patient EZ ID</label>
                            <div class="input-with-icon">
                                <i class="pi pi-id-card input-icon"></i>
                                <InputText
                                    id="ezid"
                                    v-model="lookupData.ezid"
                                    placeholder="Enter patient's EZ ID"
                                    class="enhanced-input"
                                />
                            </div>
                        </div>

                        <Button
                            label="Search Patient"
                            icon="pi pi-search"
                            @click="getInfo()"
                            class="search-btn primary"
                            :disabled="!lookupData.ezid.trim()"
                        />
                    </div>
                </div>
            </div>

            <!-- Face Recognition -->
            <div v-if="lookupValue === 'Face'" class="search-content-section">
                <div class="search-card face-search">
                    <div class="search-card-header">
                        <div class="search-icon bg-orange-100 text-orange-600">
                            <i class="pi pi-camera"></i>
                        </div>
                        <div class="search-info">
                            <h4>Face Recognition</h4>
                            <p>Search patient using facial recognition technology</p>
                        </div>
                    </div>

                    <!-- Photo Upload Area -->
                    <div class="photo-upload-section">
                        <label class="form-label">Upload Patient Photo</label>
                        <div class="photo-upload-area" :class="{ 'has-photo': selectedPhoto }">
                            <input
                                type="file"
                                ref="fileInput"
                                accept="image/*"
                                @change="onPhotoSelect"
                                class="hidden"
                                id="photoInput"
                            />
                            <label for="photoInput" class="upload-area-label">
                                <div v-if="!selectedPhoto" class="upload-placeholder">
                                    <div class="upload-icon">
                                        <i class="pi pi-camera"></i>
                                    </div>
                                    <h4 class="upload-title">Select Patient Photo</h4>
                                    <p class="upload-subtitle">Click here or drag and drop an image</p>
                                    <div class="upload-formats">
                                        <span class="format-badge">JPG</span>
                                        <span class="format-badge">PNG</span>
                                        <span class="size-info">Max 5MB</span>
                                    </div>
                                </div>
                                <div v-else class="photo-preview-card">
                                    <div class="photo-info">
                                        <div class="file-icon bg-green-100 text-green-600">
                                            <i class="pi pi-image"></i>
                                        </div>
                                        <div class="file-details">
                                            <h5 class="file-name">{{ selectedPhoto.name }}</h5>
                                            <small class="file-size">{{ (selectedPhoto.size / 1024 / 1024).toFixed(2) }} MB</small>
                                        </div>
                                    </div>
                                    <Button
                                        icon="pi pi-times"
                                        class="remove-photo-btn"
                                        outlined
                                        rounded
                                        severity="secondary"
                                        size="small"
                                        @click.stop="clearRecognitionResults"
                                    />
                                </div>
                            </label>
                        </div>
                    </div>

                    <!-- Recognition Button -->
                    <div class="recognition-button-container">
                        <Button
                            label="Recognize Face"
                            icon="pi pi-eye"
                            @click="recognizeFace()"
                            class="recognition-face-btn"
                            :loading="recognitionLoading"
                            :disabled="!selectedPhoto"
                        />
                    </div>

                    <!-- Recognition Results -->
                    <div v-if="recognitionResults.length > 0" class="recognition-results-section">
                        <div class="results-header">
                            <div class="results-title">
                                <i class="pi pi-check-circle text-green-500"></i>
                                <h4>Recognition Results ({{ recognitionResults.length }})</h4>
                            </div>
                        </div>

                        <div class="results-grid">
                            <div v-for="(result, index) in recognitionResults" :key="index" class="result-card">
                                <div class="result-content">
                                    <Avatar
                                        :label="result.ezId ? result.ezId.slice(-2) : 'U'"
                                        class="result-avatar bg-primary-500 text-white"
                                        size="large"
                                    />
                                    <div class="result-info">
                                        <h5 class="result-id">{{ result.ezId || 'Unknown ID' }}</h5>
                                        <div class="result-meta">
                                            <Tag
                                                :value="result.confidence || 'Unknown'"
                                                :severity="getConfidenceColor(result.confidence)"
                                                class="confidence-tag"
                                            />
                                            <span class="match-percentage">{{ result.match_percentage || '0%' }} match</span>
                                        </div>
                                    </div>
                                    <Button
                                        label="View Profile"
                                        icon="pi pi-user"
                                        size="small"
                                        @click="viewProfile(result.ezId)"
                                        class="view-profile-btn"
                                        :disabled="!result.ezId"
                                    />
                                </div>
                            </div>
                        </div>

                        <!-- Results Tips -->
                        <div class="results-tips">
                            <div class="tips-icon">
                                <i class="pi pi-lightbulb"></i>
                            </div>
                            <div class="tips-content">
                                <h5>Recognition Tips</h5>
                                <ul>
                                    <li>Higher confidence matches are more likely to be correct</li>
                                    <li>Multiple matches may indicate similar facial features</li>
                                    <li>Always verify identity through other means when confidence is low</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <!-- No Results - Only show after recognition attempt -->
                    <div v-else-if="hasAttemptedRecognition && recognitionResults.length === 0 && selectedPhoto && !recognitionLoading" class="no-results">
                        <div class="no-results-icon">
                            <i class="pi pi-exclamation-triangle"></i>
                        </div>
                        <h4>No Matches Found</h4>
                        <p>No matching faces found. Try with a clearer photo or use Email/EZ ID search.</p>
                    </div>

                    <!-- Example Images Link -->
                    <div class="example-link">
                        <Button
                            label="View Photo Guidelines"
                            icon="pi pi-images"
                            outlined
                            size="small"
                            @click="toggleOverlay('example-images', false)"
                        />
                    </div>
                </div>
            </div>
        </div>
    </Dialog>

    <!-- Example Images -->
    <Dialog
    v-model:visible="overlay['example-images']"
    modal
    :style="{ width: '80rem' }"
    :breakpoints="{ '1199px': '90vw', '575px': '95vw' }"
    class="example-images-dialog"
>
    <template #header>
        <div class="enhanced-dialog-header">
            <div class="header-icon-wrapper bg-green-500">
                <i class="pi pi-images text-white text-2xl"></i>
            </div>
            <div class="header-content">
                <h2 class="header-title">Photo Guidelines</h2>
                <p class="header-subtitle">Best practices for optimal facial recognition results</p>
            </div>
            <div class="header-decoration">
                <div class="decoration-dot bg-green-500"></div>
                <div class="decoration-dot bg-green-400"></div>
                <div class="decoration-dot bg-green-300"></div>
            </div>
        </div>
    </template>

    <div class="example-content">
        <!-- Good Examples Section -->
        <div class="examples-section">
            <div class="section-header">
                <i class="pi pi-check-circle text-green-500 text-lg"></i>
                <h3 class="section-title">Good Photo Examples</h3>
            </div>

            <div class="examples-grid">
                <div class="example-card good">
                    <div class="example-image-container">
                        <img
                            src="https://www.wockhardthospitals.com/wp-content/uploads/2023/05/shutterstock_365746949-scaled_11zon.webp"
                            alt="Good Example 1"
                            class="example-image"
                        />
                        <div class="example-badge success">
                            <i class="pi pi-check"></i>
                        </div>
                    </div>
                    <div class="example-info">
                        <h5>Clear & Well-lit</h5>
                        <p>Face is clearly visible with good natural lighting</p>
                    </div>
                </div>

                <div class="example-card good">
                    <div class="example-image-container">
                        <img
                            src="https://www.wockhardthospitals.com/wp-content/uploads/2023/05/shutterstock_365746949-scaled_11zon.webp"
                            alt="Good Example 2"
                            class="example-image"
                        />
                        <div class="example-badge success">
                            <i class="pi pi-check"></i>
                        </div>
                    </div>
                    <div class="example-info">
                        <h5>Front-facing</h5>
                        <p>Direct front view with minimal head tilt</p>
                    </div>
                </div>
            </div>
        </div>

        <Divider />

        <!-- Guidelines Section -->
        <div class="guidelines-section">
            <div class="section-header">
                <i class="pi pi-list text-primary-500 text-lg"></i>
                <h3 class="section-title">Photo Guidelines</h3>
            </div>

            <div class="guidelines-grid">
                <div class="guideline-card do">
                    <div class="guideline-header">
                        <i class="pi pi-check-circle text-green-500"></i>
                        <h5>Do</h5>
                    </div>
                    <ul class="guideline-list">
                        <li><i class="pi pi-check text-green-500"></i> Use good lighting (natural light preferred)</li>
                        <li><i class="pi pi-check text-green-500"></i> Face the camera directly</li>
                        <li><i class="pi pi-check text-green-500"></i> Keep face unobstructed</li>
                        <li><i class="pi pi-check text-green-500"></i> Use high-resolution images</li>
                        <li><i class="pi pi-check text-green-500"></i> Maintain neutral expression</li>
                        <li><i class="pi pi-check text-green-500"></i> Remove glasses if possible</li>
                    </ul>
                </div>

                <div class="guideline-card dont">
                    <div class="guideline-header">
                        <i class="pi pi-times-circle text-red-500"></i>
                        <h5>Don't</h5>
                    </div>
                    <ul class="guideline-list">
                        <li><i class="pi pi-times text-red-500"></i> Use blurry or low-quality images</li>
                        <li><i class="pi pi-times text-red-500"></i> Cover face with hands or objects</li>
                        <li><i class="pi pi-times text-red-500"></i> Use extreme angles or side profiles</li>
                        <li><i class="pi pi-times text-red-500"></i> Use images with harsh shadows</li>
                        <li><i class="pi pi-times text-red-500"></i> Include multiple people in frame</li>
                        <li><i class="pi pi-times text-red-500"></i> Use old or outdated photos</li>
                    </ul>
                </div>
            </div>
        </div>

        <Divider />

        <!-- Technical Requirements -->
        <div class="tech-requirements-section">
            <div class="section-header">
                <i class="pi pi-cog text-blue-500 text-lg"></i>
                <h3 class="section-title">Technical Requirements</h3>
            </div>

            <div class="tech-specs-grid">
                <div class="tech-spec-card">
                    <div class="spec-icon bg-blue-100 text-blue-600">
                        <i class="pi pi-file"></i>
                    </div>
                    <div class="spec-info">
                        <h6>Format</h6>
                        <p>JPG, PNG, GIF</p>
                    </div>
                </div>

                <div class="tech-spec-card">
                    <div class="spec-icon bg-purple-100 text-purple-600">
                        <i class="pi pi-expand"></i>
                    </div>
                    <div class="spec-info">
                        <h6>Size Limit</h6>
                        <p>Maximum 5MB</p>
                    </div>
                </div>

                <div class="tech-spec-card">
                    <div class="spec-icon bg-green-100 text-green-600">
                        <i class="pi pi-image"></i>
                    </div>
                    <div class="spec-info">
                        <h6>Resolution</h6>
                        <p>Min 300x300 pixels</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</Dialog>

        <!-- User Lookup -->
        <Dialog
        v-model:visible="overlay['user-lookup']"
        modal
        :style="{ width: '60rem' }"
        :breakpoints="{ '1199px': '85vw', '575px': '95vw' }"
        class="user-lookup-dialog"
    >
        <template #header>
            <div class="enhanced-dialog-header">
                <div class="header-icon-wrapper bg-purple-500">
                    <i class="pi pi-users text-white text-2xl"></i>
                </div>
                <div class="header-content">
                    <h2 class="header-title">User Directory</h2>
                    <p class="header-subtitle">Search for any registered user in the system</p>
                </div>
                <div class="header-decoration">
                    <div class="decoration-dot bg-purple-500"></div>
                    <div class="decoration-dot bg-purple-400"></div>
                    <div class="decoration-dot bg-purple-300"></div>
                </div>
            </div>
        </template>

        <div class="enhanced-dialog-content">
            <!-- Search Method Tabs -->
            <div class="search-method-section">
                <div class="section-header">
                    <i class="pi pi-filter text-primary-500 text-lg"></i>
                    <h3 class="section-title">Search Method</h3>
                </div>
                <div class="method-tabs">
                    <div
                        v-for="option in userlookupOptions"
                        :key="option"
                        :class="['method-tab', { 'active': userlookupValue === option }]"
                        @click="userlookupValue = option"
                    >
                        <div class="tab-icon">
                            <i :class="option === 'Email' ? 'pi pi-envelope' : 'pi pi-id-card'"></i>
                        </div>
                        <div class="tab-content">
                            <span class="tab-label">{{ option }}</span>
                            <small class="tab-description">
                                {{ option === 'Email' ? 'Search by email address' : 'Search by unique ID' }}
                            </small>
                        </div>
                        <div v-if="userlookupValue === option" class="tab-indicator"></div>
                    </div>
                </div>
            </div>

            <!-- Email Search -->
            <div v-if="userlookupValue === 'Email'" class="search-content-section">
                <div class="search-card email-search">
                    <div class="search-card-header">
                        <div class="search-icon bg-blue-100 text-blue-600">
                            <i class="pi pi-envelope"></i>
                        </div>
                        <div class="search-info">
                            <h4>Email Search</h4>
                            <p>Find user by their registered email address</p>
                        </div>
                    </div>

                    <div class="search-form">
                        <div class="form-group">
                            <label for="user-email" class="form-label">User Email Address</label>
                            <div class="input-with-icon">
                                <i class="pi pi-envelope input-icon"></i>
                                <InputText
                                    id="user-email"
                                    v-model="userlookupData.email"
                                    placeholder="Enter user's email address"
                                    class="enhanced-input"
                                />
                            </div>
                        </div>

                        <Button
                            label="Search User"
                            icon="pi pi-search"
                            @click="getUserInfo()"
                            class="search-btn primary"
                            :disabled="!userlookupData.email.trim()"
                        />
                    </div>
                </div>
            </div>

            <!-- EZ ID Search -->
            <div v-if="userlookupValue === 'EZID'" class="search-content-section">
                <div class="search-card ezid-search">
                    <div class="search-card-header">
                        <div class="search-icon bg-indigo-100 text-indigo-600">
                            <i class="pi pi-id-card"></i>
                        </div>
                        <div class="search-info">
                            <h4>EZ ID Search</h4>
                            <p>Find user by their unique EZ ID</p>
                        </div>
                    </div>

                    <div class="search-form">
                        <div class="form-group">
                            <label for="user-ezid" class="form-label">User EZ ID</label>
                            <div class="input-with-icon">
                                <i class="pi pi-id-card input-icon"></i>
                                <InputText
                                    id="user-ezid"
                                    v-model="userlookupData.ezid"
                                    placeholder="Enter user's EZ ID"
                                    class="enhanced-input"
                                />
                            </div>
                        </div>

                        <Button
                            label="Search User"
                            icon="pi pi-search"
                            @click="getUserInfo()"
                            class="search-btn primary"
                            :disabled="!userlookupData.ezid.trim()"
                        />
                    </div>
                </div>
            </div>

            <!-- Search Tips -->
            <div class="search-tips-section">
                <div class="tips-card">
                    <div class="tips-header">
                        <div class="tips-icon bg-orange-100 text-orange-600">
                            <i class="pi pi-lightbulb"></i>
                        </div>
                        <h4>Search Tips</h4>
                    </div>
                    <ul class="tips-list">
                        <li><i class="pi pi-check text-green-500"></i> Email searches are case-insensitive</li>
                        <li><i class="pi pi-check text-green-500"></i> EZ IDs are unique identifiers for each user</li>
                        <li><i class="pi pi-check text-green-500"></i> Results will show user type (Doctor, Senior, Moderator)</li>
                        <li><i class="pi pi-check text-green-500"></i> You'll be redirected to the appropriate profile page</li>
                    </ul>
                </div>
            </div>
        </div>
    </Dialog>

        <!-- SOS Overlay -->
        <Dialog v-model:visible="overlay['SOS-overlay']" modal header="🚨 Emergency SOS Alert" :style="{ width: '35rem' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
            <div class="flex flex-col items-center w-full gap-4 border-b border-surface-200 dark:border-surface-700 pb-4">
                <i class="pi pi-exclamation-circle !text-6xl text-red-500"></i>
                <div class="text-center">
                    <p class="font-semibold text-lg mb-2">Send Emergency Alert</p>
                    <p>This will immediately notify all your emergency contacts with alert notifications enabled.</p>
                    <p class="text-sm text-surface-600 dark:text-surface-400 mt-2">
                        Your location, contact details, and emergency information will be shared.
                    </p>
                </div>
            </div>

            <!-- Emergency Services Info -->
            <div class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <div class="flex items-start gap-2">
                    <i class="pi pi-info-circle text-red-600 dark:text-red-400 mt-1"></i>
                    <div class="text-sm text-red-700 dark:text-red-300">
                        <p class="font-medium mb-1">For immediate emergency:</p>
                        <ul class="space-y-1">
                            <li>• Call 108 for ambulance</li>
                            <li>• Call 100 for police</li>
                            <li>• Call 101 for fire service</li>
                        </ul>
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-center gap-3 mt-4">
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        outlined
                        severity="secondary"
                        @click="closeAllOverlays"
                        :disabled="sosLoading"
                    />
                    <Button
                        label="Send SOS Alert"
                        icon="pi pi-send"
                        severity="danger"
                        @click="sendSOS()"
                        :loading="sosLoading"
                        :disabled="sosLoading"
                    />
                </div>
            </template>
        </Dialog>

        <!-- Add Embeddings Overlay -->
        <Dialog
            v-model:visible="overlay['add-embeddings-overlay']"
            modal
            header="Register Face ID"
            :style="{ width: '500px' }"
            :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
            :closable="!embeddingsUploading"
            :dismissableMask="!embeddingsUploading"
        >
            <template #header>
                <div class="flex items-center gap-2">
                    <i class="pi pi-video text-green-500"></i>
                    <span class="text-xl font-semibold">Register Your Face ID</span>
                </div>
            </template>

            <div class="space-y-6">
                <!-- Information Panel -->
                <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div class="flex items-start gap-3">
                        <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                        <div class="text-sm text-blue-700 dark:text-blue-300">
                            <p class="font-medium mb-2">Face ID Registration</p>
                            <ul class="space-y-1">
                                <li>• Record a short video (15-30 seconds) showing your face clearly</li>
                                <li>• Look directly at the camera and move your head slightly</li>
                                <li>• Ensure good lighting and avoid shadows</li>
                                <li>• This helps doctors identify you during emergencies</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Video Upload Section -->
                <div>
                    <label class="block text-surface-900 dark:text-surface-0 text-lg font-medium mb-3">
                        Upload Your Video
                    </label>

                    <div class="border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
                        <input
                            type="file"
                            ref="videoInput"
                            accept="video/*"
                            @change="onEmbeddingsVideoSelect"
                            class="hidden"
                            id="embeddingsVideoInput"
                        />
                        <label for="embeddingsVideoInput" class="cursor-pointer">
                            <div class="flex flex-col items-center gap-3">
                                <i class="pi pi-video text-4xl text-surface-400 hover:text-primary-500 transition-colors"></i>
                                <div>
                                    <p class="text-surface-700 dark:text-surface-300 font-medium">
                                        {{ embeddingsVideo ? 'Video Selected' : 'Click to select your video' }}
                                    </p>
                                    <small class="text-surface-500 dark:text-surface-400">
                                        Supported formats: MP4, AVI, MOV (Max: 50MB)
                                    </small>
                                </div>
                            </div>
                        </label>
                    </div>
                </div>

                <!-- Selected Video Preview -->
                <div v-if="embeddingsVideo" class="p-4 bg-surface-50 dark:bg-surface-800 rounded-lg">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <i class="pi pi-video text-primary-500"></i>
                            <div>
                                <p class="font-medium text-surface-900 dark:text-surface-0">{{ embeddingsVideo.name }}</p>
                                <small class="text-surface-500 dark:text-surface-400">
                                    {{ (embeddingsVideo.size / 1024 / 1024).toFixed(2) }} MB
                                </small>
                            </div>
                        </div>
                        <Button
                            icon="pi pi-times"
                            size="small"
                            outlined
                            severity="secondary"
                            @click="clearEmbeddingsVideo"
                            v-tooltip.top="'Remove video'"
                            :disabled="embeddingsUploading"
                        />
                    </div>
                </div>

                <!-- Guidelines -->
                <div class="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <div class="flex items-start gap-3">
                        <i class="pi pi-exclamation-triangle text-yellow-600 dark:text-yellow-400 mt-1"></i>
                        <div class="text-sm text-yellow-700 dark:text-yellow-300">
                            <p class="font-medium mb-2">Recording Guidelines</p>
                            <ul class="space-y-1">
                                <li>• Face should be clearly visible throughout the video</li>
                                <li>• Avoid wearing masks, sunglasses, or head coverings</li>
                                <li>• Record in well-lit environment</li>
                                <li>• Keep the camera steady</li>
                                <li>• Look directly at the camera</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-3 mt-6">
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        outlined
                        @click="closeAllOverlays"
                        :disabled="embeddingsUploading"
                    />
                    <Button
                        label="Register Face ID"
                        icon="pi pi-check"
                        severity="success"
                        @click="registerFaceEmbeddings"
                        :loading="embeddingsUploading"
                        :disabled="!embeddingsVideo"
                    />
                </div>
            </template>
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

/* Custom video input styling */
#embeddingsVideoInput {
    display: none;
}

/* Video upload zone styling */
.video-upload-zone {
    transition: all 0.3s ease;
}

.video-upload-zone:hover {
    border-color: var(--primary-500);
    background-color: var(--primary-50);
}

:global(.p-dark) .video-upload-zone:hover {
    background-color: var(--primary-900);
}

/* Enhanced Dialog Styles */
.enhanced-lookup-dialog :deep(.p-dialog-content),
.example-images-dialog :deep(.p-dialog-content),
.user-lookup-dialog :deep(.p-dialog-content) {
    padding: 0;
}

.enhanced-dialog-header {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 2rem;
    background: linear-gradient(135deg, var(--surface-50), var(--surface-100));
    border-bottom: 1px solid var(--surface-200);
    position: relative;
    overflow: hidden;
}

.header-icon-wrapper {
    width: 4rem;
    height: 4rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    z-index: 2;
}

.header-content {
    flex: 1;
    z-index: 2;
}

.header-title {
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    color: var(--text-color);
}

.header-subtitle {
    font-size: 1rem;
    color: var(--text-color-secondary);
    margin: 0;
}

.header-decoration {
    display: flex;
    gap: 0.5rem;
    z-index: 1;
}

.decoration-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    opacity: 0.3;
}

.enhanced-dialog-content {
    padding: 2rem;
}

/* Search Method Section */
.search-method-section {
    margin-bottom: 2rem;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    color: var(--text-color);
}

.method-tabs {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.method-tab {
    position: relative;
    padding: 1.5rem;
    border: 2px solid var(--surface-300);
    border-radius: 16px;
    background: var(--surface-0);
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.method-tab:hover {
    border-color: var(--primary-400);
    box-shadow: 0 4px 20px rgba(var(--primary-500-rgb), 0.1);
    transform: translateY(-2px);
}

.method-tab.active {
    border-color: var(--primary-500);
    background: linear-gradient(135deg, var(--primary-50), var(--primary-100));
    box-shadow: 0 8px 30px rgba(var(--primary-500-rgb), 0.2);
}

.tab-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 12px;
    background: var(--surface-100);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: var(--text-color-secondary);
    transition: all 0.3s ease;
}

.method-tab.active .tab-icon {
    background: var(--primary-500);
    color: white;
}

.tab-content {
    flex: 1;
}

.tab-label {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-color);
    display: block;
}

.tab-description {
    color: var(--text-color-secondary);
    font-size: 0.9rem;
}

.tab-indicator {
    position: absolute;
    top: -2px;
    right: -2px;
    width: 12px;
    height: 12px;
    background: var(--primary-500);
    border-radius: 50%;
    border: 2px solid var(--surface-0);
}

/* Search Content Section */
.search-content-section {
    margin-bottom: 2rem;
}

.search-card {
    background: var(--surface-50);
    border: 1px solid var(--surface-200);
    border-radius: 20px;
    padding: 2rem;
    transition: all 0.3s ease;
}

.search-card:hover {
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.1);
    border-color: var(--primary-200);
}

.search-card-header {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.search-icon {
    width: 4rem;
    height: 4rem;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
}

.search-info h4 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: var(--text-color);
}

.search-info p {
    font-size: 1rem;
    color: var(--text-color-secondary);
    margin: 0;
}

/* Form Styles */
.form-group {
    margin-bottom: 1.5rem;
}

.form-label {
    display: block;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-color);
    margin-bottom: 0.75rem;
}

.input-with-icon {
    position: relative;
}

.input-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-color-secondary);
    z-index: 2;
}

.enhanced-input {
    width: 100%;
    padding: 1rem 1rem 1rem 3rem;
    border: 2px solid var(--surface-300);
    border-radius: 12px;
    font-size: 1rem;
    background: var(--surface-0);
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.enhanced-input:hover {
    border-color: var(--primary-400);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.enhanced-input:focus {
    border-color: var(--primary-500);
    box-shadow: 0 0 0 4px rgba(var(--primary-500-rgb), 0.1), 0 4px 16px rgba(0, 0, 0, 0.1);
    outline: none;
}

.search-btn {
    width: 100%;
    padding: 1rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 12px;
    transition: all 0.3s ease;
}

.search-btn.primary {
    background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
    border: none;
    color: white;
}

.search-btn.primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(var(--primary-500-rgb), 0.3);
}

/* Photo Upload Styles */
.photo-upload-section {
    margin-bottom: 2rem;
}

.photo-upload-area {
    border: 3px dashed var(--surface-400);
    border-radius: 16px;
    background: var(--surface-100);
    transition: all 0.3s ease;
    overflow: hidden;
}

.photo-upload-area:hover {
    border-color: var(--primary-500);
    background: var(--primary-50);
}

.upload-area-label {
    display: block;
    cursor: pointer;
    padding: 3rem 2rem;
    text-align: center;
}

.upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.upload-icon {
    width: 5rem;
    height: 5rem;
    background: var(--primary-100);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: var(--primary-600);
    margin-bottom: 1rem;
}

.upload-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
}

.upload-subtitle {
    color: var(--text-color-secondary);
    margin: 0;
}

.upload-formats {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 1rem;
}

.format-badge {
    padding: 0.25rem 0.5rem;
    background: var(--primary-100);
    color: var(--primary-700);
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
}

.size-info {
    color: var(--text-color-secondary);
    font-size: 0.875rem;
}

.photo-preview-card {
    padding: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--surface-0);
    border-radius: 12px;
}

.photo-info {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.file-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.file-name {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 0.25rem 0;
}

.file-size {
    color: var(--text-color-secondary);
}

/* Recognition Button Styles - Complete override with highest specificity */
.recognition-button-container {
    margin: 2rem 0;
    width: 100%;
    display: block;
    clear: both;
    position: relative;
    z-index: 10;
}

.recognition-face-btn {
    width: 100%;
    min-height: 3rem;
    padding: 1rem 2rem;
    font-size: 1.1rem;
    font-weight: 700;
    border-radius: 12px;
    border: 2px solid #3b82f6;
    background-color: #3b82f6;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    text-transform: none;
    letter-spacing: normal;
}

.recognition-face-btn:hover:not(:disabled) {
    background-color: #2563eb;
    border-color: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.recognition-face-btn:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.recognition-face-btn:disabled {
    background-color: #9ca3af;
    border-color: #9ca3af;
    color: #6b7280;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
    opacity: 1;
}

.recognition-face-btn:focus {
    outline: 2px solid #3b82f6;
    outline-offset: 2px;
}

/* Override any PrimeVue button styles that might interfere */
.recognition-button-container .p-button,
.recognition-button-container .p-component {
    width: 100% !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: static !important;
}

.recognition-button-container .p-button:disabled {
    opacity: 1 !important;
    background-color: #9ca3af !important;
    border-color: #9ca3af !important;
    color: #6b7280 !important;
}

.recognition-button-container .p-button .p-button-label {
    font-weight: 700 !important;
}

.recognition-button-container .p-button .p-button-icon {
    font-size: 1.1rem !important;
}

/* Dark mode support */
:global(.p-dark) .recognition-face-btn {
    background-color: #3b82f6;
    border-color: #3b82f6;
    color: #ffffff;
}

:global(.p-dark) .recognition-face-btn:hover:not(:disabled) {
    background-color: #2563eb;
    border-color: #2563eb;
}

:global(.p-dark) .recognition-face-btn:disabled {
    background-color: #4b5563;
    border-color: #4b5563;
    color: #9ca3af;
}

/* Recognition Results */
.recognition-results-section {
    margin-top: 2rem;
    padding: 2rem;
    background: var(--surface-0);
    border: 1px solid var(--surface-200);
    border-radius: 16px;
}

.results-header {
    margin-bottom: 1.5rem;
}

.results-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.results-title h4 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
}

.results-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
}

.result-card {
    background: var(--surface-50);
    border: 1px solid var(--surface-200);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.result-card:hover {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.result-content {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.result-avatar {
    flex-shrink: 0;
}

.result-info {
    flex: 1;
}

.result-id {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 0.5rem 0;
}

.result-meta {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.confidence-tag {
    font-weight: 600;
}

.match-percentage {
    color: var(--text-color-secondary);
    font-size: 0.9rem;
}

.view-profile-btn {
    flex-shrink: 0;
}

/* Results Tips */
.results-tips {
    display: flex;
    gap: 1rem;
    padding: 1.5rem;
    background: var(--blue-50);
    border-radius: 12px;
    border-left: 4px solid var(--blue-500);
}

.tips-icon {
    color: var(--blue-500);
    font-size: 1.5rem;
}

.tips-content h5 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--blue-700);
    margin: 0 0 0.75rem 0;
}

.tips-content ul {
    margin: 0;
    padding-left: 1.5rem;
    color: var(--blue-600);
}

.tips-content li {
    margin-bottom: 0.5rem;
    line-height: 1.4;
}

/* No Results */
.no-results {
    text-align: center;
    padding: 3rem;
    color: var(--text-color-secondary);
}

.no-results-icon {
    font-size: 4rem;
    color: var(--orange-400);
    margin-bottom: 1rem;
}

.no-results h4 {
    font-size: 1.25rem;
    color: var(--text-color);
    margin: 0 0 0.5rem 0;
}

/* Example Link */
.example-link {
    text-align: center;
    margin-top: 2rem;
}

/* Example Images Dialog Styles */
.example-content {
    padding: 2rem;
}

.examples-section {
    margin-bottom: 3rem;
}

.examples-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.example-card {
    background: var(--surface-0);
    border: 2px solid var(--surface-200);
    border-radius: 20px;
    overflow: hidden;
    transition: all 0.3s ease;
}

.example-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    border-color: var(--primary-300);
}

.example-image-container {
    position: relative;
    height: 250px;
    overflow: hidden;
}

.example-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.example-badge {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.25rem;
    border: 3px solid white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.example-badge.success {
    background: var(--green-500);
}

.example-info {
    padding: 1.5rem;
}

.example-info h5 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 0.5rem 0;
}

.example-info p {
    color: var(--text-color-secondary);
    line-height: 1.5;
    margin: 0;
}

/* Guidelines Section */
.guidelines-section {
    margin-bottom: 3rem;
}

.guidelines-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.guideline-card {
    background: var(--surface-50);
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid var(--surface-200);
}

.guideline-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}

.guideline-header h5 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
}

.guideline-card.do .guideline-header h5 {
    color: var(--green-600);
}

.guideline-card.dont .guideline-header h5 {
    color: var(--red-600);
}

.guideline-list {
    margin: 0;
    padding: 0;
    list-style: none;
}

.guideline-list li {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    line-height: 1.5;
    color: var(--text-color-secondary);
}

/* Technical Requirements */
.tech-requirements-section {
    margin-bottom: 2rem;
}

.tech-specs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
}

.tech-spec-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    background: var(--surface-50);
    border: 1px solid var(--surface-200);
    border-radius: 12px;
}

.spec-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    flex-shrink: 0;
}

.spec-info h6 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0 0 0.25rem 0;
}

.spec-info p {
    color: var(--text-color-secondary);
    margin: 0;
}

/* Search Tips Section */
.search-tips-section {
    margin-top: 2rem;
}

.tips-card {
    background: var(--orange-50);
    border: 1px solid var(--orange-200);
    border-radius: 16px;
    padding: 2rem;
}

.tips-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.tips-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.tips-header h4 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
}

.tips-list {
    margin: 0;
    padding: 0;
    list-style: none;
}

.tips-list li {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    line-height: 1.5;
    color: var(--text-color-secondary);
}

/* Dark mode adjustments */
:global(.p-dark) .enhanced-dialog-header {
    background: linear-gradient(135deg, var(--surface-800), var(--surface-700));
    border-bottom-color: var(--surface-600);
}

:global(.p-dark) .search-card {
    background: var(--surface-800);
    border-color: var(--surface-600);
}

:global(.p-dark) .photo-upload-area {
    background: var(--surface-800);
    border-color: var(--surface-600);
}

:global(.p-dark) .photo-upload-area:hover {
    background: var(--surface-700);
}

:global(.p-dark) .enhanced-input {
    background: var(--surface-900);
    border-color: var(--surface-600);
    color: var(--text-color);
}

:global(.p-dark) .enhanced-input:hover {
    border-color: var(--primary-400);
    background: var(--surface-800);
}

:global(.p-dark) .enhanced-input:focus {
    border-color: var(--primary-500);
    background: var(--surface-900);
}

/* Recognition Button Styles - Enhanced with higher specificity */
.recognition-button-section {
    margin: 1.5rem 0 !important;
    display: block !important;
}

.recognition-btn {
    width: 100% !important;
    padding: 1rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
    background: linear-gradient(135deg, var(--primary-500), var(--primary-600)) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(var(--primary-500-rgb), 0.2) !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

.recognition-btn:not(:disabled) {
    background: linear-gradient(135deg, var(--primary-500), var(--primary-600)) !important;
    color: white !important;
}

.recognition-btn:not(:disabled):hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(var(--primary-500-rgb), 0.3) !important;
    background: linear-gradient(135deg, var(--primary-600), var(--primary-700)) !important;
}

.recognition-btn:disabled {
    background: var(--surface-400) !important;
    color: var(--surface-600) !important;
    cursor: not-allowed !important;
    box-shadow: none !important;
    transform: none !important;
    opacity: 0.6 !important;
}

/* Force button visibility in all states */
.recognition-button-section .p-button {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

.recognition-button-section .p-button:disabled {
    opacity: 0.6 !important;
}

:global(.p-dark) .recognition-btn:disabled {
    background: var(--surface-600) !important;
    color: var(--surface-400) !important;
}

/* Additional button container styling to ensure visibility */
.recognition-button-section {
    background: transparent !important;
    position: relative !important;
    z-index: 1 !important;
}

/* Responsive Design */
@media (max-width: 768px) {
    .enhanced-dialog-header {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
        padding: 1.5rem;
    }

    .method-tabs {
        grid-template-columns: 1fr;
    }

    .guidelines-grid {
        grid-template-columns: 1fr;
    }

    .examples-grid {
        grid-template-columns: 1fr;
    }

    .tech-specs-grid {
        grid-template-columns: 1fr;
    }

    .enhanced-dialog-content {
        padding: 1rem;
    }

    .example-content {
        padding: 1rem;
    }
}

@media (max-width: 480px) {
    .header-title {
        font-size: 1.5rem;
    }

    .header-subtitle {
        font-size: 0.9rem;
    }

    .search-card {
        padding: 1.5rem;
    }

    .upload-area-label {
        padding: 2rem 1rem;
    }
}
</style>

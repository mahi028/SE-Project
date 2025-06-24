<script setup>
    import { ref } from 'vue';
    import { RouterLink } from 'vue-router';

    const props = defineProps({
        page: String,
    })

    const overlay = ref({
        'patient-lookup': false,
    })

    const doctorWidgets = ref([
        {
            id: 1,
            label: 'Patient Lookup',
            desc: 'Find Patients info from email or just their face.',
            action: 'overlay',
            type: 'patient-lookup',
        },
    ])

    const toggleOverlay = (type)=>{
        for (const key in overlay.value) {
            overlay.value[key] = false
        }
        if (type in overlay.value) {
            overlay.value[type] = true
        }
    }

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
</script>
<template>
    <div class="col-span-12 lg:col-span-6 xl:col-span-3" v-for="widget in props.page == 'doctor' ? doctorWidgets : seniorWidgets" key="id">
        <RouterLink v-if="widget.action=='redirect'" :to="widget.redirect">
        <div class="card mb-0" >
                <div class="flex justify-between mb-4">
                    <div>
                        <span class="block text-muted-color font-medium mb-4">{{ widget.label }}</span>
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
                    <span class="block text-muted-color font-medium mb-4">{{ widget.label }}</span>
                </div>
                <div class="flex items-center justify-center bg-blue-100 dark:bg-blue-400/10 rounded-border" style="width: 2.5rem; height: 2.5rem">
                    <Button type="button" @click="toggleOverlay(widget.type)" icon="pi pi-search" rounded></Button>
                </div>
            </div>
            <span class="text-muted-color">{{ widget.desc }}</span>
        </div>
    </div>
    <div class="col-span-12 lg:col-span-6 xl:col-span-3" v-for="fakeItem in props.page == 'doctor' ? doctorWidgets.length % 4 : seniorWidgets.length % 4"></div>
    <Dialog v-model:visible="overlay['patient-lookup']" modal header="Get Patient's Medical Info " :style="{ width: '45rem' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }">
        <span>Do it here</span>
    </Dialog>
</template>

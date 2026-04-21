<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-indigo-600 text-white shadow-md">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold tracking-tight">🧠 Cognition Web</h1>
        <div class="flex items-center space-x-4">
          <span class="text-indigo-200 text-sm hidden md:inline">Powered by Docker Model Runner & Pydantic-AI</span>
          <button @click="openSettings" class="text-indigo-200 hover:text-white transition-colors" title="Paramètres Moteur">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          </button>
        </div>
      </div>
    </header>

    <main class="flex-grow max-w-7xl mx-auto w-full px-4 py-8 relative">

      <!-- MODAL DE NOTIFICATION CENTRAL (Overlay) -->
      <div v-if="notification.show" class="fixed inset-0 flex items-center justify-center bg-slate-900/40 z-[70] animate-fade-in backdrop-blur-sm" @click="notification.show = false">
        <div class="bg-white p-8 rounded-2xl shadow-2xl max-w-sm w-full text-center transform transition-all scale-100" @click.stop>
          <div class="mx-auto flex items-center justify-center h-16 w-16 mb-4 rounded-full" 
               :class="notification.type === 'error' ? 'bg-rose-100 text-rose-500' : (notification.type === 'info' ? 'bg-indigo-100 text-indigo-500' : 'bg-emerald-100 text-emerald-500')">
            <svg v-if="notification.type === 'success'" class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            <svg v-else-if="notification.type === 'error'" class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            <svg v-else class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          <h3 class="text-xl font-black text-slate-800 mb-2">{{ notification.title }}</h3>
          <p class="text-slate-600 text-sm mb-6">{{ notification.message }}</p>
          <button @click="notification.show = false" 
                  class="w-full py-3 rounded-xl font-bold text-white transition-colors shadow-md"
                  :class="notification.type === 'error' ? 'bg-rose-500 hover:bg-rose-600' : (notification.type === 'info' ? 'bg-indigo-500 hover:bg-indigo-600' : 'bg-emerald-500 hover:bg-emerald-600')">
            Compris !
          </button>
        </div>
      </div>

      <!-- ICÔNE DE NOTIFICATION BATCH (Bottom-right) -->
      <div v-if="batchNotification.show" 
           class="fixed bottom-4 right-4 z-50 animate-pulse">
        <div class="relative">
          <div class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
            {{ batchNotification.count }}
          </div>
          <button @click="goToProposals" 
                  class="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-all hover:scale-110">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- PANEL LATÉRAL DES PARAMÈTRES (Slide-Over) -->
      <div v-if="isSettingsOpen" class="fixed inset-0 z-[60] flex justify-end">
        <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity" @click="closeSettings"></div>
        <div class="relative w-full max-w-md bg-white h-full shadow-2xl flex flex-col animate-fade-in">
          <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50">
            <h2 class="text-xl font-bold text-slate-800">Paramètres Moteur</h2>
            <button @click="closeSettings" class="text-slate-400 hover:text-slate-600"><svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg></button>
          </div>
          <div class="flex-grow overflow-y-auto p-6 space-y-8">
            <section>
              <h3 class="text-sm font-bold tracking-wider text-indigo-500 uppercase mb-4 flex items-center"><span class="mr-2">🧠</span> Cerveau IA</h3>
              <div class="space-y-4">
                <div>
                  <label class="block text-xs font-semibold text-slate-600 mb-1">Fournisseur</label>
                  <select v-model="settingsForm.llm_provider" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none"><option value="ollama">Ollama (Local)</option><option value="gemini">Gemini (Cloud)</option></select>
                </div>
                <div v-if="settingsForm.llm_provider === 'ollama'">
                  <label class="block text-xs font-semibold text-slate-600 mb-1">Ollama Host</label>
                  <input v-model="settingsForm.ollama_host" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none">
                </div>
                <div v-if="settingsForm.llm_provider === 'ollama'">
                  <label class="block text-xs font-semibold text-slate-600 mb-1">Modèle Local</label>
                  <input v-model="settingsForm.ollama_model" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none">
                </div>
                <div>
                  <label class="block text-xs font-semibold text-slate-600 mb-1">Température ({{ settingsForm.temperature }})</label>
                  <input v-model.number="settingsForm.temperature" type="range" min="0" max="1" step="0.1" class="w-full accent-indigo-600">
                </div>
              </div>
            </section>
            <section>
              <h3 class="text-sm font-bold tracking-wider text-slate-500 uppercase mb-4 flex items-center"><span class="mr-2">🛡️</span> Opérations (DevOps)</h3>
              <div class="flex items-center justify-between bg-slate-50 p-3 rounded-lg border border-slate-200">
                <div><p class="text-sm font-bold text-slate-700">Mode DRY_RUN</p><p class="text-xs text-slate-500">Simuler sans consommer VRAM</p></div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="settingsForm.dry_run" class="sr-only peer">
                  <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>
            </section>
            <section>
              <h3 class="text-sm font-bold tracking-wider text-emerald-500 uppercase mb-4 flex items-center"><span class="mr-2">👁️</span> Traitement Visuel</h3>
              <div class="space-y-4">
                <div>
                  <label class="block text-xs font-semibold text-slate-600 mb-1">Résolution ({{ settingsForm.image_resolution }}px)</label>
                  <input v-model.number="settingsForm.image_resolution" type="range" min="336" max="1200" step="16" class="w-full accent-emerald-500">
                </div>
                <div>
                  <label class="block text-xs font-semibold text-slate-600 mb-1">Qualité: {{ settingsForm.image_quality }}%</label>
                  <input v-model.number="settingsForm.image_quality" type="range" min="10" max="100" step="5" class="w-full accent-emerald-500">
                </div>
              </div>
            </section>
          </div>
          <div class="p-6 border-t border-slate-100 bg-white">
            <button @click="saveSettings" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-xl shadow-md transition-colors">Enregistrer & Appliquer à chaud</button>
          </div>
        </div>
      </div>

      <!-- MENU DE NAVIGATION -->
      <div v-if="!proposal && !isLoading && !isBatchLoading" class="flex justify-center space-x-6 mb-8 mt-2 border-b border-slate-200 pb-2">
        <button @click="navigateTo('/')" 
                :class="currentRoute === '/' ? 'text-indigo-600 border-b-2 border-indigo-600 font-bold' : 'text-slate-500 hover:text-indigo-500 font-medium'" 
                class="px-4 py-2 pb-3 -mb-[9px] transition-all">
          📥 Inbox Upload
        </button>
        <button @click="navigateTo('/proposals')" 
                :class="currentRoute === '/proposals' ? 'text-emerald-600 border-b-2 border-emerald-600 font-bold' : 'text-slate-500 hover:text-emerald-500 font-medium'" 
                class="px-4 py-2 pb-3 -mb-[9px] transition-all flex items-center">
          📋 Propositions en attente
          <span v-if="pendingProposals.length > 0" class="ml-2 bg-emerald-100 text-emerald-700 py-0.5 px-2.5 rounded-full text-xs font-bold shadow-sm">{{ pendingProposals.length }}</span>
        </button>
      </div>

      <!-- VUE 1 : UPLOAD INBOX -->
      <div v-if="currentRoute === '/' && !proposal && !isLoading && !isBatchLoading" class="animate-fade-in space-y-6">
        <div class="border-4 border-dashed border-slate-300 rounded-xl p-20 flex flex-col items-center justify-center text-slate-500 hover:border-indigo-400 hover:bg-indigo-50 transition-colors cursor-pointer"
             @dragover.prevent
             @drop.prevent="handleDrop"
             @click="triggerFileInput">
          <svg class="w-16 h-16 mb-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
          <p class="text-xl font-medium">Glissez votre capture d'écran ici</p>
          <p class="text-sm mt-2">ou cliquez pour parcourir</p>
          <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="handleFileSelect">
        </div>

        <div class="border-4 border-dashed border-emerald-300 rounded-xl p-10 flex flex-col items-center justify-center text-emerald-600 hover:border-emerald-500 hover:bg-emerald-50 transition-colors cursor-pointer"
             @dragover.prevent
             @drop.prevent="handleBatchDrop"
             @click="triggerBatchFileInput">
          <svg class="w-10 h-10 mb-2 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
          <p class="text-lg font-medium">Mode Batch : Glissez PLUSIEURS images ici</p>
          <p class="text-xs mt-1">L'optimisation et la compression webP 1200px seront prises en charge par l'IA en arrière-plan.</p>
          <input type="file" ref="batchFileInput" class="hidden" accept="image/*" multiple @change="handleBatchFileSelect">
        </div>
      </div>

      <!-- VUE 2 : DASHBOARD DES PROPOSITIONS -->
      <div v-if="currentRoute === '/proposals' && !proposal && !isLoading && !isBatchLoading" class="animate-fade-in">
        <div v-if="isFetchingProposals" class="flex justify-center py-20">
          <div class="animate-spin rounded-full h-12 w-12 border-b-4 border-emerald-500"></div>
        </div>
        
        <div v-else-if="pendingProposals.length === 0" class="text-center py-20 bg-slate-50 rounded-2xl border border-slate-200">
           <svg class="w-16 h-16 mx-auto mb-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
           <h3 class="text-xl font-bold text-slate-500">Aucune proposition en attente</h3>
           <p class="text-slate-400 mt-2">Uploadez des images en mode batch pour générer de nouvelles propositions.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="prop in pendingProposals" :key="prop.id" 
               @click="selectProposal(prop)"
               class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-xl transition-all cursor-pointer group hover:-translate-y-1 overflow-hidden relative">
            <div class="absolute top-0 left-0 w-full h-1" 
                 :class="prop.action === 'create' ? 'bg-emerald-400' : (prop.action === 'append' ? 'bg-indigo-400' : 'bg-rose-400')"></div>
            <div class="flex justify-between items-start mb-3 mt-1">
              <span class="text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded"
                    :class="prop.action === 'create' ? 'bg-emerald-100 text-emerald-800' : (prop.action === 'append' ? 'bg-indigo-100 text-indigo-800' : 'bg-rose-100 text-rose-800')">
                {{ prop.action }}
              </span>
              <span v-if="prop.is_new_domain" class="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-1 rounded-full">New Domain!</span>
            </div>
            <h3 class="font-bold text-slate-800 text-lg mb-1 truncate group-hover:text-indigo-600 transition-colors" :title="prop.title">{{ prop.title }}</h3>
            <p class="text-xs text-slate-500 mb-3 truncate font-mono bg-slate-50 p-1 rounded inline-block">{{ prop.domain }}</p>
            <p class="text-sm text-slate-600 line-clamp-2 mt-2 leading-snug">{{ prop.reasoning }}</p>
            <div class="mt-4 flex items-center justify-between text-xs text-slate-400 border-t border-slate-100 pt-3">
              <span class="flex items-center"><svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg> {{ prop.source_image }}</span>
              <span class="flex items-center font-bold text-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity">Traiter <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg></span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isLoading || isBatchLoading" class="flex flex-col items-center justify-center py-20">
        <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mb-4"></div>
        <p v-if="isLoading" class="text-lg font-medium text-slate-600 animate-pulse">L'agent IA analyse l'image en local...</p>
        <p v-if="isBatchLoading" class="text-lg font-medium text-emerald-600 animate-pulse">{{ batchMsg || "Préparation du lot..." }}</p>
      </div>

      <div v-if="proposal && !isLoading" class="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fade-in relative">
        <button @click="reset" class="absolute -top-12 left-0 text-slate-500 hover:text-indigo-600 flex items-center font-medium transition-colors">
          <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg> Retour
        </button>

        <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-col">
          <h2 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3">Source Visuelle</h2>
          <div class="flex-grow flex items-center justify-center bg-slate-100 rounded-lg overflow-hidden relative">
            <img v-if="previewUrl" :src="previewUrl" alt="Capture à analyser" class="max-w-full max-h-[600px] object-contain">
            <div v-else class="flex flex-col items-center justify-center text-slate-400 p-8 text-center">
              <svg class="w-16 h-16 mb-2 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
              <p class="font-bold">Image archivée en local</p>
              <p class="text-xs">{{ proposal.source_image }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex flex-col space-y-4">

          <div class="bg-indigo-50 border-l-4 border-indigo-500 p-4 rounded-r-lg">
            <p class="text-sm text-indigo-900"><strong>🧠 Raisonnement de l'IA :</strong> {{ proposal.reasoning }}</p>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Titre</label>
              <input v-model="proposal.title" type="text" class="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none">
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">
                Domaine
                <span v-if="proposal.is_new_domain" class="ml-2 bg-amber-100 text-amber-800 text-[10px] px-2 py-0.5 rounded-full">NOUVEAU !</span>
              </label>
              <input v-model="proposal.domain" type="text" class="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Action</label>
              <select v-model="proposal.action" class="w-full border border-slate-300 rounded px-3 py-2 outline-none">
                <option value="create">CREATE (Nouveau fichier)</option>
                <option value="append">APPEND (Fichier existant)</option>
                <option value="ignore">IGNORE (Bruit)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Tags consolidés</label>
              <input v-model="mergedTags" type="text" class="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none">
            </div>
          </div>

          <div v-if="proposal.action === 'append'" class="animate-fade-in">
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Fichier Cible</label>
            <input v-model="proposal.target_file" type="text" class="w-full border border-emerald-300 bg-emerald-50 rounded px-3 py-2 outline-none">
          </div>

          <div class="flex-grow flex flex-col">
            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Contenu Markdown</label>
            <textarea v-model="proposal.markdown_content" rows="10" class="w-full flex-grow border border-slate-300 rounded px-3 py-2 font-mono text-sm focus:ring-2 focus:ring-indigo-500 outline-none resize-none"></textarea>
          </div>

          <div class="flex space-x-4 pt-4 border-t border-slate-100">
            <button @click="reject" class="flex-1 bg-white border border-rose-500 text-rose-600 font-bold py-3 rounded-lg hover:bg-rose-50 transition-colors">
              ❌ Rejeter
            </button>
            <button @click="publish" class="flex-1 bg-emerald-500 text-white font-bold py-3 rounded-lg hover:bg-emerald-600 shadow-md hover:shadow-lg transition-all">
              ✅ Approuver & Envoyer (Notion)
            </button>
          </div>

        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const isSettingsOpen = ref(false)
const settingsForm = ref({
  llm_provider: "ollama",
  ollama_host: "",
  ollama_model: "",
  temperature: 0.0,
  dry_run: false,
  image_resolution: 768,
  image_quality: 65
})

const openSettings = () => { isSettingsOpen.value = true; }
const closeSettings = () => { isSettingsOpen.value = false; }

const loadSettings = async () => {
  try {
    const res = await fetch('/api/v2/settings')
    if (res.ok) {
      settingsForm.value = await res.json()
    }
  } catch (e) {
    console.error("Erreur chargement settings API", e)
  }
}

const saveSettings = async () => {
  try {
    const res = await fetch('/api/v2/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settingsForm.value)
    })
    if (res.ok) {
      const result = await res.json()
      settingsForm.value = result.settings
      closeSettings()
      showNotification("⚙️ Moteur Mis à Jour", "Les nouveaux paramètres IA ont été appliqués à chaud.", "success")
    }
  } catch (e) {
    showNotification("Erreur de sauvegarde", "Impossible de contacter l'API.", "error")
  }
}

const initWebSocket = () => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${wsProtocol}//${window.location.host}/ws/batch-status`
  
  websocket.value = new WebSocket(wsUrl)
  
  websocket.value.onopen = () => {
    console.log('WebSocket connecté pour les notifications batch')
  }
  
  websocket.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'BATCH_COMPLETED') {
        batchNotification.value.show = true
        batchNotification.value.count = data.count
        showNotification("Batch Terminé", data.message, "success")
      }
    } catch (e) {
      console.error('Erreur parsing notification WS:', e)
    }
  }
  
  websocket.value.onclose = () => {
    setTimeout(initWebSocket, 3000)
  }
  
  websocket.value.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
}

const currentRoute = ref(window.location.pathname)
const pendingProposals = ref([])
const isFetchingProposals = ref(false)

const fetchProposals = async () => {
  isFetchingProposals.value = true
  try {
    const res = await fetch('/api/v2/proposals')
    if (res.ok) {
      const data = await res.json()
      pendingProposals.value = data.proposals || []
    }
  } catch(e) {
    console.error('Erreur fetchProposals', e)
  } finally {
    isFetchingProposals.value = false
  }
}

const navigateTo = (path) => {
  if (currentRoute.value !== path) {
    window.history.pushState({}, '', path)
    currentRoute.value = path
    if (path === '/proposals') fetchProposals()
  }
}

onMounted(() => {
  loadSettings()
  initWebSocket()
  
  if (currentRoute.value === '/proposals') {
    fetchProposals()
  }

  window.addEventListener('popstate', () => {
    currentRoute.value = window.location.pathname
    if (currentRoute.value === '/proposals') fetchProposals()
  })
})

onUnmounted(() => {
  if (websocket.value) {
    websocket.value.close()
  }
})

const fileInput = ref(null)
const isLoading = ref(false)
const isBatchLoading = ref(false)
const batchMsg = ref(null)
const batchFileInput = ref(null)
const proposal = ref(null)
const previewUrl = ref(null)
const errorMsg = ref(null)

const notification = ref({ show: false, type: 'success', title: '', message: '' })
const batchNotification = ref({ show: false, count: 0 })
const websocket = ref(null)

const showNotification = (title, message, type = 'success') => {
  notification.value = { show: true, type, title, message }
}

// Fusionner les tags existants et proposés pour l'édition facile
const mergedTags = computed({
  get: () => {
    if (!proposal.value) return ""
    const eTags = proposal.value.existing_tags ? proposal.value.existing_tags.split(',') : []
    const pTags = proposal.value.proposed_new_tags ? proposal.value.proposed_new_tags.split(',') : []
    return [...eTags, ...pTags].filter(t => t.trim() !== '').join(', ')
  },
  set: (val) => {
    // Si l'utilisateur modifie l'input, on stocke tout dans existing_tags pour la soumission
    proposal.value.existing_tags = val
    proposal.value.proposed_new_tags = ""
  }
})

const triggerFileInput = () => fileInput.value.click()

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) processFile(file)
}

const handleDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) processFile(file)
}

const triggerBatchFileInput = () => batchFileInput.value.click()

const handleBatchFileSelect = (event) => {
  processBatchFiles(event.target.files)
}

const handleBatchDrop = (event) => {
  processBatchFiles(event.dataTransfer.files)
}

const processBatchFiles = async (filesList) => {
  if (!filesList || filesList.length === 0) return;
  const files = Array.from(filesList).filter(f => f.type.startsWith('image/'))
  if (files.length === 0) return;

  isBatchLoading.value = true;
  batchMsg.value = `Envoi de ${files.length} images vers l'inbox...`

  const formData = new FormData()
  files.forEach(f => formData.append('files', f))

  try {
    const uploadRes = await fetch('/api/v2/upload/inbox', {
      method: 'POST',
      body: formData
    })
    
    const result = await uploadRes.json()

    if (result.status === "success") {
      batchMsg.value = `Lancement du traitement IA par lots en arrière-plan...`
      await fetch('/api/v2/analyze/batch', { method: 'POST' })
      showNotification("Batch Démarré", `Succès ! ${files.length} images envoyées à l'inbox. Le système IA les traite en tâche de fond.`, "success")
    } else {
      throw new Error(result.detail || "Erreur inconnue lors de l'upload.")
    }
  } catch (error) {
    showNotification("Erreur Batch", error.message, "error")
  } finally {
    isBatchLoading.value = false;
    batchMsg.value = null;
    if (batchFileInput.value) batchFileInput.value.value = "";
  }
}

const processFile = async (file) => {
  previewUrl.value = URL.createObjectURL(file)
  isLoading.value = true
  errorMsg.value = null

  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch('/api/v2/analyze', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (result.status === "success") {
      proposal.value = result.data
    } else if (result.status === "ignored") {
      showNotification("Image Ignorée", result.reasoning || result.message || "Bruit", "info")
      reset()
    } else {
      throw new Error(result.detail || "Erreur inconnue")
    }
  } catch (error) {
    showNotification("Réseau / Backend", error.message, "error")
    reset()
  } finally {
    isLoading.value = false
  }
}

const selectProposal = (prop) => {
  proposal.value = prop
  previewUrl.value = null // Car on traite en mode backend
}

const publish = async () => {
  try {
    const payload = {
      title: proposal.value.title,
      domain: proposal.value.domain,
      action: proposal.value.action,
      target_file: proposal.value.target_file,
      tags: mergedTags.value,
      markdown_content: proposal.value.markdown_content
    }

    const response = await fetch(`/api/v2/publish/${proposal.value.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (response.ok) {
      showNotification("Sauvegarde Réussie", "Le document est sauvegardé localement et envoyé vers Notion.", "success")
      reset()
    } else {
      showNotification("Erreur Sauvegarde", "Erreur lors de l'approbation.", "error")
    }
  } catch (e) {
    showNotification("Réseau", e.message, "error")
  }
}

const reject = () => {
  fetch(`/api/v2/reject/${proposal.value.id}`, { method: 'POST' })
  reset()
}

const reset = () => {
  proposal.value = null
  previewUrl.value = null
  if (fileInput.value) fileInput.value.value = ""
  if (currentRoute.value === '/proposals') {
    fetchProposals()
  }
}

const goToProposals = () => {
  batchNotification.value.show = false
  navigateTo('/proposals')
}
</script>
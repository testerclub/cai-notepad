<template>
  <section class="main container-flex">
    <!-- NEW NOTE  -->
    <div class="col-md-12">
      <header>
        <template v-if="!isCreateNew">
          <section class="card bg-light mx-1 my-2">
            <div class="card-body py-2">
              <button @click="createNewNote" class="btn btn-primary btn-raised">New note</button>
            </div>
          </section>
        </template>
        <template v-else>
          <note-editor
            :note="newNote"
            :isCreating="true"
            v-on:doneEdit="addNewNote"
            v-on:cancelEdit="clearNewNote"
          ></note-editor>
        </template>
      </header>
    </div>

    <!-- PINNED NOTES -->
    <section class v-show="hasPinned">
      <div class="col-12">
        <header>Pinned</header>
        <note-container
          v-for="note in pinnedNotes"
          :key="note.id"
          :note="note"
          :isCreateNew="isCreateNew"
          :editingNote="editingNote"
          v-on:startEdit="startEdit"
          v-on:doneEdit="doneEdit"
          v-on:cancelEdit="cancelEdit"
        />
      </div>
    </section>
    <!-- DEFAULT -->

    <section class="col-12">
      <header v-show="hasOthers && (hasArchived || hasPinned)">Others</header>
      <note-container
        v-for="note in notes"
        :key="note.id"
        :note="note"
        :isCreateNew="isCreateNew"
        :editingNote="editingNote"
        v-on:startEdit="startEdit"
        v-on:doneEdit="doneEdit"
        v-on:cancelEdit="cancelEdit"
      />
    </section>
    <!-- ARCHIVED -->
    <section class="col-12">
      <header v-show="hasArchived">Archived</header>
      <note-container
        v-for="note in archivedNotes"
        :key="note.id"
        :note="note"
        :isCreateNew="isCreateNew"
        :editingNote="editingNote"
        v-on:startEdit="startEdit"
        v-on:doneEdit="doneEdit"
        v-on:cancelEdit="cancelEdit"
      />
    </section>
  </section>
</template>

<script>
import { mapState, mapActions, mapMutations, mapGetters } from 'vuex';

import NoteEditor from './editor.vue';
import NoteContainer from './note-container.vue';

export default {
  name: 'notes',

  components: {
    NoteContainer,
    NoteEditor
  },

  created () {
    this._fetchAndUpdate(this.$route);
  },

  data () {
    return {
      isCreateNew: false,
      newNote: {
        title: '',
        content: '',
        is_pinned: false,
        category: null
      },
      editingNote: null,
      lastSelectedCategory: null
    };
  },

  computed: {
    ...mapGetters('Notes', {
      notes: 'defaultItems',
      pinnedNotes: 'pinnedItems',
      archivedNotes: 'archivedItems'
    }),
    ...mapState('Notes', {
      selectedCategoryId: 'categoryFilter',
      selectedMilestoneId: 'milestoneFilter'
    }),
    ...mapGetters('Categories', {
      category: 'category'
    }),
    hasPinned () {
      return this.pinnedNotes !== null && this.pinnedNotes.length > 0;
    },
    hasOthers () {
      return this.notes !== null && this.notes.length > 0;
    },
    hasArchived () {
      return this.archivedNotes !== null && this.archivedNotes.length > 0;
    },

    selectedCategory () {
      return this.category(this.selectedCategoryId);
    }
  },

  methods: {
    _fetchAndUpdate (route) {
      this.$store.dispatch('Notes/updateFilters', {
        categoryId: route.query.category ? route.query.category : 'all',
        milestoneId: route.query.milesonte ? route.query.milesonte : 'all'
      });
      // TODO: selectedCategoryId shall be the ID we send to the backend
      const self = this;
      this.$store.dispatch('Notes/fetchAll').then(() => {
        self.lastSelectedCategory = self.selectedCategory
          ? self.selectedCategory.id
          : null;
        self.newNote.category = self.lastSelectedCategory;
        console.log(
          'filtering',
          self.selectedCategory,
          self.selectedCategoryId
        );
      });
    },

    createNewNote () {
      if (this.editingNote) {
        if (!confirm('Previous changes will lost. Are you sure?')) {
          return;
        }
      }
      this.newNote.category = this.selectedCategory;
      this.isCreateNew = true;
    },

    clearNewNote () {
      this.newNote = {
        title: '',
        content: '',
        category: this.selectedCategory
      };
      this.isCreateNew = false;
    },

    addNewNote () {
      this.$store.dispatch('Notes/addNew', this.newNote);
      this.clearNewNote();
    },

    startEdit (note) {
      console.log('a');
      if (this.isCreateNew || this.editingNote) {
        if (!confirm('Previous changes will lost. Are you sure?')) {
          return;
        }
      }
      this.editingNote = Object.assign({}, note);
    },
    doneEdit (note) {
      console.log('b');
      if (!this.editingNote) return;
      this.$store.dispatch('Notes/edit', this.editingNote);
      this.editingNote = null;
    },
    cancelEdit (note) {
      console.log('c');
      if (!this.editingNote) return;
      this.editingNote = null;
    }
  },

  watch: {
    $route (to, from) {
      this._fetchAndUpdate(to);
    }
  }
};
</script>

<style lang="scss" scoped>
</style>

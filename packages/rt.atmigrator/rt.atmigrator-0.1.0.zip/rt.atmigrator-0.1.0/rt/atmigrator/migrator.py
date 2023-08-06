# -*- coding: utf-8 -*-


def makeFolderMigrator(context, src_type, dst_type):
    """ generate a migrator for the given at-based folderish portal type """
    from Products.contentmigration.archetypes import InplaceATFolderMigrator

    class ATFolderMigrator(InplaceATFolderMigrator):
        src_portal_type = src_type
        dst_portal_type = dst_type

    return ATFolderMigrator


def makeContentMigrator(context, src_type, dst_type):
    """ generate a migrator for the given at-based portal type """
    from Products.contentmigration.archetypes import InplaceATItemMigrator

    class ATContentMigrator(InplaceATItemMigrator):
        src_portal_type = src_type
        dst_portal_type = dst_type

    return ATContentMigrator


def migrateContents(context, src_type, dst_type):
    from Products.contentmigration.walker import CustomQueryWalker
    #BBB: i can't find a better way to know if a given portal_type is folderish or not
    is_folderish = False
    temp_obj = context.restrictedTraverse('portal_factory/%s/tmp_id' % src_type)
    if temp_obj:
        plone_view = temp_obj.restrictedTraverse('@@plone')
        if plone_view.isStructuralFolder():
            is_folderish = True
    portal_types = context.portal_types
    src_infos = portal_types.getTypeInfo(src_type)
    dst_infos = portal_types.getTypeInfo(dst_type)
    if is_folderish:
        migrator = makeFolderMigrator(context,
                                     src_type,
                                     dst_type,)
    else:
        migrator = makeContentMigrator(context,
                                      src_type,
                                      dst_type,)
    if migrator:
        migrator.src_meta_type = src_infos.content_meta_type
        migrator.dst_meta_type = dst_infos.content_meta_type
        walker = CustomQueryWalker(context, migrator,
                                  src_portal_type=src_type,
                                  dst_portal_type=dst_type,
                                  use_savepoint=True)
        walker.go()
        walk_infos = {'error': walker.errors,
                      'msg': walker.getOutput().splitlines(),
                      'counter': walker.counter}
        return walk_infos

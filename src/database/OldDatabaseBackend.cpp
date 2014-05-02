#include "OldDatabaseBackend.h"
#include "core/global.h"

void OldDatabaseBackend::submit(DBOperation *operation)
{
	if(operation->m_type == DBOperation::OperationType::CREATE_OBJECT)
	{
		ObjectData dbo(operation->m_dclass->get_id());
		dbo.fields = operation->m_set_fields;

		doid_t doid = create_object(dbo);
		if(doid == INVALID_DO_ID || doid < m_min_id || doid > m_max_id)
		{
			operation->on_failure();
		}
		else
		{
			operation->on_complete(doid);
		}
	}
	else if(operation->m_type == DBOperation::OperationType::DELETE_OBJECT)
	{
		delete_object(operation->m_doid);
		operation->on_complete();
	}
	else if(operation->m_type == DBOperation::OperationType::GET_OBJECT ||
	        operation->m_type == DBOperation::OperationType::GET_FIELDS)
	{
		ObjectData dbo;
		if(!get_object(operation->m_doid, dbo))
		{
			operation->on_failure();
			return;
		}

		const dclass::Class *dclass = g_dcf->get_class_by_id(dbo.dc_id);
		if(!dclass)
		{
			operation->on_failure();
			return;
		}

		DBObjectSnapshot *snap = new DBObjectSnapshot();
		snap->m_dclass = dclass;
		snap->m_fields = dbo.fields;
		operation->on_complete(snap);
		// snap is deleted by on_complete.
	}
}